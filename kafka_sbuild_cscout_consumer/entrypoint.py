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


def find_error(err):
    """Return the contents from an error log file if exists.
    """
    error_file = '/callgraph/{}'.format(err)
    if os.path.isfile(error_file):
        with open(error_file, 'r') as f:
            return f.read()
    return None


class Analyser:
    """Produce a call graph from a Debian Package Release.
    """

    def __init__(self, topic, error_topic, producer, release):
        self.status = ''
        self.error_msg = {}
        self.topic = topic
        self.error_topic = error_topic
        self.producer = producer
        self.package = release['source']
        self.version = release['source_version']
        self.dist = release['release']
        self.arch = release['arch']
        self.dir_name = '{}-{}'.format(self.package, self.version)
        self.url = snap_url.format(self.package, self.version)
        self.urls = []

    def analyse(self):
        try:
            self._download_files()
            self._run_sbuild()
            self._check_analysis_result()
            self._produce_cg_to_kafka()
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
                    raise AnalyserError("Error during request")
                return resp.content
        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(
                url, str(e))
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
            print("Cannot find .dsc file or found multiple")
            raise AnalyserError("Cannot find .dsc file or found multiple")
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
            with open('/callgraph/report', 'r') as file:
                self.status = file.read().strip()
        except FileNotFoundError:
            print("File not found: /callgraph/report")
            raise AnalyserError("File not found: /callgraph/report")
        if self.status == 'done':
            print("{}: Call graph generated".format(
                str(datetime.datetime.now()))
            )
        else:
            print("{}: An error occurred during call graph generation".format(
                str(datetime.datetime.now()))
            )
            raise AnalyserError("An error occurred during cg generation")

    def _save_error_messages(self, errors):
        """Save error messages in self.error_msg dictionary.
        """
        self.error_msg[self.status] = {}
        for error in errors:
            self.error_msg[self.status][error] = find_error(error)

    def _detect_error_messages(self):
        """Detect which error occurred.
        """
        if self.status == 'failed-csmake':
            self._save_error_messages(['csmake_error'])
        elif self.status == 'failed-cscout':
            self._save_error_messages(['csmake_warnings', 'cscout_error'])
        elif self.status == 'failed-empty':
            self._save_error_messages(['csmake_warnings', 'cscout_warnings'])
        elif self.status == 'failed-fcan':
            self._save_error_messages(['fcan_error'])

    def _produce_error_to_kafka(self):
        """Push error to kafka topic.
        """
        print("{}: Push error message to kafka topic".format(
            str(datetime.datetime.now()))
        )
        self._detect_error_messages()
        self.producer.send(self.error_topic, json.dumps(self.error_msg))

    def _produce_cg_to_kafka(self):
        """Push call graph to kafka topic.
        """
        with open('/callgraph/can_cgraph.json', 'r') as f:
            call_graph = json.load(f)
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
        max_poll_records=1,
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
