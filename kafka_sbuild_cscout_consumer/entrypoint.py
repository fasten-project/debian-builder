import os
import sys
import glob
import time
import datetime
import json
import argparse
import subprocess as sp
from kafka import KafkaProducer
from kafka import KafkaConsumer
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


archive_mirror = 'https://snapshot.debian.org'
snap_url = archive_mirror + '/package/{}/{}/'
download_url = archive_mirror + '{}'


class AnalyserError(Exception):
    """Custom exception for Analyzer.
    """


def create_dir(dir_name):
    """Safely create directory package-version.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


class Analyser:
    """Produce a call graph from a Debian Package Release.
    """

    def __init__(self, topic, error_topic, producer, release):
        self.status = ''
        self.topic = topic
        self.error_topic = error_topic
        self.producer = producer
        self.package = release['source']
        self.version = release['source_version']
        self.dist = release['release']
        self.arch = release['arch']
        self.dir_name = '{}-{}-{}-{}'.format(
                self.package, self.dist, self.arch, self.version
        )
        self.callgraph_dir = '/{}/{}/{}/{}/{}/'.format(
            'callgraphs', self.package, self.dist, self.version, self.arch
        )
        self.url = snap_url.format(self.package, self.version)
        self.urls = []
        self.error_msg = {
                'package': self.package,
                'version': self.version,
                'dist': self.dist,
                'arch': self.arch,
                'phase':'', 
                'type':'', 
                'message':'', 
                'datetime':''
        }
        self.binary_pkgs = []

    def analyse(self):
        try:
            self._download_files()
            self._run_sbuild()
            self._check_analysis_result()
        except AnalyserError:
            self._produce_error_to_kafka()

    def _retrieve_page(self, url):
        """Returns a Debian Snapshot HTML page.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if resp.status_code != 200:
                    print('Error during requests to {0} : status {1}'.format(
                        url, resp.status_code
                    ))
                    self.error_msg['phase'] = 'downloading'
                    self.error_msg['message'] = 'Url {}: status {}'.format(
                        url, resp.status_code
                    )
                    raise AnalyserError("Error during request")
                return resp.content
        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(
                url, str(e))
            )
            self.error_msg['phase'] = 'downloading'
            self.error_msg['message'] = 'Url {}: error {}'.format(
                url, str(e)
            )
            raise AnalyserError("Error during request")

    def _parse_page(self):
        """Parses a Debian Snapshot HTML page and parses the sources URLs.
        """
        html = BeautifulSoup(self.page, 'html.parser')
        source_files = html.select('dl')[0]
        for source in source_files.select('dd'):
            for block in source.select('dl'):
                self.urls.append(block.select('a')[0]['href'])

    def _download_file(self, url):
        """Download file (usually .dsc, .tar.xz, and .debian.tar.xz).
        """
        try:
            contents = self._retrieve_page(download_url.format(url))
        except AnalyserError:
            raise
        filename = '{}/{}'.format(self.dir_name, url[url.rfind('/')+1:])
        with open(filename, 'wb') as f:
            f.write(contents)

    def _download_files(self):
        """Download files needed to run sbuild.
        """
        # Find urls
        try:
            self.page = self._retrieve_page(self.url)
        except AnalyserError:
            raise
        self._parse_page()

        # Create directory to save the files
        create_dir(self.dir_name)

        # Download the files
        for source_file_url in self.urls:
            try:
                self._download_file(source_file_url)
            except AnalyserError:
                raise

    def _run_sbuild(self):
        """Run sbuild to produce call graph.
        """
        print("{}: Run sbuild for {}, dist={}, arch={}".format(
            str(datetime.datetime.now()),
            self.dir_name,
            self.dist,
            self.arch
        ))
        # Change working directory to directory with source files
        old_cwd = os.getcwd()
        os.chdir(self.dir_name)

        # Find the .dsc file
        dsc = glob.glob("*.dsc")
        if len(dsc) != 1:
            message = 'Cannot find .dsc file or found multiple'
            print(message)
            self.error_msg['phase'] = 'run_sbuild'
            self.error_msg['message'] = message
            raise AnalyserError(message)
        dsc = dsc[0]

        sbuild_options = [
            'sbuild',
            '--apt-update',
            '--no-apt-upgrade',
            '--no-apt-distupgrade',
            '--batch',
            '--stats-dir=/var/log/sbuild/stats',
            '--dist={}'.format(self.dist),
            '--arch={}'.format(self.arch),
            dsc
        ]
        # Run sbuild
        cmd = sp.Popen(sbuild_options, stdout=sp.PIPE, stderr=sp.STDOUT)
        stdout, _ = cmd.communicate()
        #  print("sbuild stdout\n" + stdout.decode(encoding='utf-8'))
        os.chdir(old_cwd)

    def _check_analysis_result(self):
        """Checks if call graph generated successfully.
        """
        try:
            with open(self.callgraph_dir + 'report', 'r') as fd:
                for line in fd:
                    if line.startswith('#'):
                        continue
                    line = line.strip()
                    log = line.split(': ')
                    if log[0] == 'build':
                        if log[1] == 'failed':
                            self.error_msg['phase'] = 'build'
                            self.error_msg['message'] = 'Build failed'
                            raise AnalyserError('Build failed')
                    elif log[0] == 'detect_binaries':
                        if log[1] == 'failed':
                            self.error_msg['phase'] = 'detect_binaries'
                            self.error_msg['message'] = 'No binaries found'
                            raise AnalyserError('No binaries found')
                    elif log[0] == 'analysis':
                        if log[2] == 'failed':
                            self.error_msg['phase'] = 'analysis'
                            self.error_msg['type'] = log[3]
                            self.error_msg['message'] = log[1]
                            self._produce_error_to_kafka()
                    elif log[0] == 'produce_debs':
                        if log[1] == 'failed':
                            self.error_msg['phase'] = 'detect_binaries'
                            self.error_msg['message'] = 'Produce debian packages failed'
                            raise AnalyserError('Produce debian packages failed')
                    elif log[0] == 'detect_packages':
                        self.binary_pkgs = log[1].split(' ')
                    elif log[0] == 'produce_callgraph':
                        if log[2] == 'failed':
                            self.error_msg['phase'] = 'produce_callgraph'
                            self.error_msg['type'] = log[3]
                            self.error_msg['message'] = log[1]
                            self._produce_error_to_kafka()
                        if log[2] == 'success':
                            self.status = 'done'
                            pkg = log[1]
                            path = "{}/{}/".format(
                                self.callgraph_dir, pkg
                            )
                            print("{}: Push call graph for {} to kafka topic".format(
                                str(datetime.datetime.now()), pkg)
                            )
                            self._produce_cg_to_kafka(path)
        except FileNotFoundError:
            message = "File not found: " + self.callgraph_dir + "/report"
            print(message)
            self.error_msg['phase'] = 'report'
            self.error_msg['message'] = message
            raise AnalyserError(message)
        if self.status == 'done':
            print("{}: Call graph generated".format(
                str(datetime.datetime.now()))
            )

    def _produce_error_to_kafka(self):
        """Push error to kafka topic.
        """
        print("{}: Push error message to kafka topic: {}: {}: {}".format(
            self.error_msg['phase'],
            self.error_msg['type'],
            self.error_msg['message'],
            str(datetime.datetime.now()))
        )
        self.error_msg['datetime'] = str(datetime.datetime.now())
        self.producer.send(self.error_topic, json.dumps(self.error_msg))

    def _produce_cg_to_kafka(self, path):
        """Push call graph to kafka topic.
        """
        try:
            with open(path + 'fcg.json', 'r') as f:
                call_graph = json.load(f)
        except FileNotFoundError:
            message = "File not found: " + path + "fcg.json"
            print(message)
            self.error_msg['phase'] = 'read_fcg'
            self.error_msg['message'] = message
            raise AnalyserError(message)
        self.producer.send(self.topic, json.dumps(call_graph))


def exit_with_error():
    """Exit with return code 1.
    """
    sys.exit(1)


def consume_from_kafka(in_topic, out_topic, err_topic, servers, group):
    consumer = KafkaConsumer(
        in_topic,
        bootstrap_servers=servers.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=servers.split(','),
        value_serializer=lambda x: x.encode('utf-8')
    )
    for message in consumer:
        release = message.value
        print("{}: Consuming {}".format(
            str(datetime.datetime.now()), release)
        )
        analyser = Analyser(out_topic, err_topic, producer, release)
        analyser.analyse()


def get_parser():
    parser = argparse.ArgumentParser(
        "Consume Debian packages releases messages of a Kafka topic."
    )
    parser.add_argument('in_topic', type=str, help="Kafka topic to read from.")
    parser.add_argument(
        'out_topic',
        type=str,
        help="Kafka topic to write to."
    )
    parser.add_argument(
        'err_topic',
        type=str,
        help="Kafka topic to write errors to."
    )
    parser.add_argument(
        'bootstrap_servers',
        type=str,
        help="Kafka servers, comma separated."
    )
    parser.add_argument(
        'group',
        type=str,
        help="Kafka consumer group to which the consumer belongs."
    )
    parser.add_argument(
        'sleep_time',
        type=int,
        help="Time to sleep in between each scrape (in sec)."
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    in_topic = args.in_topic
    out_topic = args.out_topic
    err_topic = args.err_topic
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time

    # Run forever
    while True:
        consume_from_kafka(in_topic, out_topic, err_topic, bootstrap_servers,
                           group)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
