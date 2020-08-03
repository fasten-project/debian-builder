import os
import sys
import glob
import time
import datetime
import json
import argparse
import shutil
import urllib
import requests
import subprocess as sp
from fasten.plugins.kafka import KafkaPlugin
from fasten.plugins.base import PluginError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


archive_mirror = 'https://snapshot.debian.org'
snap_url = archive_mirror + '/package/{}/{}/'
download_url = archive_mirror + '{}'


class IntermediatePluginError(Exception):
    """Error that occurs on non fatal cases
    """

def create_dir(dir_name):
    """Safely create directory package-version.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


class PackageState():
    """A structure that contains the state for a package.
    """
    def __init__(self, record):
        self.record = record
        self.package = record['source']
        self.version = record['source_version']
        self.dist = record['release']
        self.arch = record['arch']
        self.dir_name = '{}-{}-{}-{}'.format(
            self.package, self.dist, self.arch, self.version
        )
        self.callgraph_dir = '/{}/{}/{}/{}/{}/'.format(
            'callgraphs', self.package, self.dist, self.version, self.arch
        )
        self.url = snap_url.format(
            self.package, urllib.parse.quote(self.version)
        )
        self.urls = []
        self.profiling_data = {'times': {}}
        self.binary_pkgs = []
        self.old_cwd = os.getcwd()
        self.err = {'error': {}}
        self.error_msg = self.err['error']
        self.status = ""


class CScoutKafkaPlugin(KafkaPlugin):
    """Produce C call graphs from Debian package releases.
    """
    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic
        self.produce_topic = produce_topic
        self.log_topic = log_topic
        self.error_topic = error_topic
        self.group_id = group_id
        self.set_consumer()
        self.set_producer()
        # State per package
        self.state = None

    def name(self):
        return "CScoutKafkaPlugin"

    def description(self):
        return "A Kafka plug-in that uses CScout to produce C call graphs"

    def version(self):
        return "0.0.1"

    def free_resource(self):
        pass

    def _retrieve_page(self, url):
        """Returns a Debian Snapshot HTML page.
        """
        try:
            session = requests.Session()
            retry = Retry(connect=5, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            with closing(session.get(url, stream=True)) as resp:
                if resp.status_code != 200:
                    m = '{0}: Error during requests to {1} : status {2}'.format(
                        str(datetime.datetime.now()),
                        url, resp.status_code
                    )
                    self.log(m)
                    self.state.error_msg['phase'] = 'retrieving the url'
                    self.state.error_msg['message'] = 'Url {}: status {}'.format(
                        url, resp.status_code
                    )
                    raise PluginError("Error during request")
                return resp.content
        except RequestException as e:
            m = '{}: Error during requests to {} : {}'.format(
                str(datetime.datetime.now()),
                url,
                str(e)
            )
            self.log(m)
            self.state.error_msg['phase'] = 'retrieving the url'
            self.state.error_msg['message'] = 'Url {}: error {}'.format(
                url, str(e)
            )
            raise PluginError("Error during request")

    def _parse_page(self, page):
        """Parses a Debian Snapshot HTML page and parses the sources URLs.
        """
        html = BeautifulSoup(page, 'html.parser')
        source_files = html.select('dl')[0]
        for source in source_files.select('dd'):
            for block in source.select('dl'):
                self.state.urls.append(block.select('a')[0]['href'])

    def _download_file(self, url):
        """Download file (usually .dsc, .tar.xz, and .debian.tar.xz).
        """
        try:
            contents = self._retrieve_page(
                download_url.format(url)
            )
        except PluginError:
            raise
        unquoted_url = urllib.parse.unquote(url[url.rfind('/')+1:])
        filename = '{}/{}'.format(self.state.dir_name, unquoted_url)
        with open(filename, 'wb') as f:
            f.write(contents)

    def download(self):
        """Download the source code of project
        """
        # Find urls
        try:
            page = self._retrieve_page(self.state.url)
        except PluginError:
            raise
        self._parse_page(page)

        # Create directory to save the files
        create_dir(self.state.dir_name)

        # Download the files
        for source_file_url in self.state.urls:
            try:
                self._download_file(source_file_url)
            except PluginError:
                raise

    def _run_sbuild(self):
        """Run sbuild to produce call graph.
        """
        m = "{}: Run sbuild for {}, dist={}, arch={}".format(
            str(datetime.datetime.now()),
            self.state.dir_name,
            self.state.dist,
            self.state.arch
        )
        self.log(m)
        # Change working directory to directory with source files
        os.chdir(self.state.dir_name)

        # Find the .dsc file
        dsc = glob.glob("*.dsc")
        if len(dsc) != 1:
            message = 'Cannot find .dsc file or found multiple'
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.log(m)
            self.state.error_msg['phase'] = 'run_sbuild'
            self.state.error_msg['message'] = message
            raise PluginError(message)
        dsc = dsc[0]

        sbuild_options = [
            'sbuild',
            '--apt-update',
            '--no-apt-upgrade',
            '--no-apt-distupgrade',
            '--batch',
            '--stats-dir=/var/log/sbuild/stats',
            '--dist={}'.format(self.state.dist),
            '--arch={}'.format(self.state.arch),
            dsc
        ]
        # Run sbuild
        cmd = sp.Popen(sbuild_options, stdout=sp.PIPE, stderr=sp.STDOUT)
        stdout, _ = cmd.communicate()
        if cmd.returncode == 1:
            message = 'Sbuild failed:\n{}'.format(stdout.decode(encoding='utf-8'))
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.state.error_msg['phase'] = 'run_sbuild'
            self.state.error_msg['message'] = message
            raise PluginError(message)
        os.chdir(self.state.old_cwd)

    def _check_analysis_result(self):
        """Checks if call graph generated successfully.
        """
        try:
            with open(self.state.callgraph_dir + 'report', 'r') as fd:
                lines = [l.strip().split(': ') for l in fd
                        if not l.startswith('#')]
                for log in lines:
                    if log[0] == 'time_elapsed':
                        if len(log) >= 3:
                            self.state.profiling_data['times'][log[1]] = log[2]
                for log in lines:
                    if log[0] == 'build':
                        if log[1] == 'failed':
                            self.state.error_msg['phase'] = 'build'
                            self.state.error_msg['message'] = 'Build failed'
                            raise PluginError('Build failed')
                    elif log[0] == 'detect_binaries':
                        if log[1] == 'failed':
                            self.state.error_msg['phase'] = 'detect_binaries'
                            self.state.error_msg['message'] = 'No binaries found'
                            raise PluginError('No binaries found')
                    elif log[0] == 'analysis':
                        if log[2] == 'failed':
                            self.state.error_msg['phase'] = 'analysis'
                            self.state.error_msg['type'] = log[3]
                            self.state.error_msg['message'] = log[1]
                            self._produce_error_to_kafka()
                    elif log[0] == 'produce_debs':
                        if log[1] == 'failed':
                            self.state.error_msg['phase'] = 'detect_binaries'
                            self.state.error_msg['message'] = 'Produce debian packages failed'
                            raise PluginError('Produce debian packages failed')
                    elif log[0] == 'detect_packages':
                        self.state.binary_pkgs = log[1].split(' ')
                    elif log[0] == 'produce_callgraph':
                        if log[2] == 'failed':
                            self.state.error_msg['phase'] = 'produce_callgraph'
                            self.state.error_msg['type'] = log[3]
                            self.state.error_msg['message'] = log[1]
                            self._produce_error_to_kafka()
                        if log[2] == 'success':
                            self.state.status = 'done'
                            pkg = log[1]
                            path = "{}/{}/".format(
                                self.state.callgraph_dir, pkg
                            )
                            m = "{}: Push call graph for {} to kafka topic".format(
                                str(datetime.datetime.now()), pkg
                            )
                            self.log(m)
                            self._produce_cg_to_kafka(path)
        except FileNotFoundError:
            message = "File not found: " + self.state.callgraph_dir + "report"
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.log(m)
            self.state.error_msg['phase'] = 'report'
            self.state.error_msg['message'] = message
            raise PluginError(message)
        if self.state.status == 'done':
            m = "{}: Call graph generated".format(
                str(datetime.datetime.now())
            )
            self.log(m)

    def _cleanup(self):
        """Remove the downloaded sources and the call graphs from the
        filesystem.
        """
        m = "{}: Cleanup".format(
            str(datetime.datetime.now())
        )
        self.log(m)
        try:
            shutil.rmtree(self.state.dir_name)
        except OSError as e:
            m = "{}: {} - {}.".format(
                str(datetime.datetime.now()), e.filename, e.strerror
            )
            self.log(m)
        try:
            shutil.rmtree(self.state.callgraph_dir)
        except OSError as e:
            m = "{}: {} - {}.".format(
                str(datetime.datetime.now()), e.filename, e.strerror
            )
            self.log(m)

    def _produce_error_to_kafka(self):
        """Push error to kafka topic.
        """
        m = "{}: Push error message to kafka topic: {}: {}".format(
            str(datetime.datetime.now()),
            self.state.error_msg['phase'],
            self.state.error_msg['message']
        )
        self.log(m)
        self.state.error_msg['datetime'] = str(datetime.datetime.now())
        self.state.error_msg['profiling_data'] = self.state.profiling_data
        message = self.create_message(self.state.record, self.state.err)
        self.emit_message(self.error_topic, message, "error", "")

    def _produce_cg_to_kafka(self, path):
        """Push call graph to kafka topic.
        """
        try:
            with open(path + 'fcg.json', 'r') as f:
                call_graph = json.load(f)
        except FileNotFoundError:
            message = "File not found: " + path + "fcg.json"
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.log(m)
            self.state.error_msg['phase'] = 'read_fcg'
            self.state.error_msg['message'] = message
            raise PluginError(message)
        call_graph['profiling_data'] = self.state.profiling_data
        message = self.create_message(self.state.record, {"payload": call_graph})
        self.emit_message(self.produce_topic, message, "succeed", "")

    def consume(self, record):
        """First download the sources, then run sbuild, and finally check the
           results.
        """
        # State of package
        self.state = PackageState(record)
        # Begin
        message = self.create_message(record, {"status": "begin"})
        self.emit_message(self.log_topic, message, "begin", "")
        try:
            self.download()
            self._run_sbuild()
            self._check_analysis_result()
            message = self.create_message(record, {"status": "success"})
            self.emit_message(self.log_topic, message, "complete", "")
        except PluginError:
            self._produce_error_to_kafka()
            message = self.create_message(record, {"status": "failed"})
            self.emit_message(self.log_topic, message, "failed", "")
        os.chdir(self.state.old_cwd)
        self._cleanup()
        # End
        self.state = None


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
        'log_topic',
        type=str,
        help="Kafka topic to write logs to."
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
    log_topic = args.log_topic if args.log_topic else False
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time

    plugin = CScoutKafkaPlugin(bootstrap_servers, in_topic, out_topic,
                               log_topic, err_topic, group)

    # Run forever
    while True:
        plugin.consume_messages()
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
