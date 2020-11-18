# Copyright (c) 2018-2020 FASTEN.
#
# This file is part of FASTEN
# (see https://www.fasten-project.eu/).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
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
import ast
import subprocess as sp
from distutils.dir_util import copy_tree
from fasten.plugins.kafka import KafkaPlugin
from fasten.plugins.base import PluginError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


archive_mirror = 'https://snapshot.debian.org'
snap_url = archive_mirror + '/package/{}/{}/'
deb_url = 'http://deb.debian.org/debian/pool/main/{}/{}/{}'
download_url = archive_mirror + '{}'


deb_lookup = [
    '0', '2', '3', '4', '6', '7', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z'
]
# Only packages from l can be in different directories
deb_lookup_l = [
    'lib3', 'liba', 'libb', 'libc', 'libd', 'libe', 'libf',
    'libg', 'libh', 'libi', 'libj', 'libk', 'libl', 'libm', 'libn', 'libo',
    'libp', 'libq', 'libr', 'libs', 'libt', 'libu', 'libv', 'libw', 'libx',
    'liby', 'libz'
]

class IntermediatePluginError(Exception):
    """Error that occurs on non fatal cases
    """

def create_dir(dir_name):
    """Safely create directory package-version.
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


def retrieve_page(url):
    """Retrieve a web page.

    Args:
        url
    Returns:
        status: boolean (true->success, false->failed)
        content (str) or error (dict)
        log message
    """
    try:
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        error_msg = {}

        with closing(session.get(url, stream=True)) as resp:
            if resp.status_code != 200:
                m = '{0}: Error during requests to {1} : status {2}'.format(
                    str(datetime.datetime.now()),
                    url, resp.status_code
                )
                error_msg['phase'] = 'retrieving the url'
                error_msg['message'] = 'Url {}: status {}'.format(
                    url, resp.status_code
                )
                return False, error_msg, m
            return True, resp.content, None
    except RequestException as e:
        m = '{}: Error during requests to {} : {}'.format(
            str(datetime.datetime.now()),
            url,
            str(e)
        )
        error_msg['phase'] = 'retrieving the url'
        error_msg['message'] = 'Url {}: error {}'.format(
            url, str(e)
        )
        return False, error_msg, m


def download_file(url, dir_name):
    """Download file (usually .dsc, .tar.xz, and .debian.tar.xz).
    """
    status, result, message = retrieve_page(url)

    if not status:
        return status, result, message

    unquoted_url = urllib.parse.unquote(url[url.rfind('/')+1:])
    filename = '{}/{}'.format(dir_name, unquoted_url)
    with open(filename, 'wb') as f:
        f.write(result)
    return True, None, None


def parse_page_snap(page):
    """Parses a Debian Snapshot HTML page and parses the sources URLs.
    """
    urls = []
    html = BeautifulSoup(page, 'html.parser')
    source_files = html.select('dl')[0]
    for source in source_files.select('dd'):
        for block in source.select('dl'):
            urls.append(block.select('a')[0]['href'])
    return urls


def download_snap(source, version, dir_name):
    url = snap_url.format(
        source, urllib.parse.quote(version)
    )
    # Find urls
    status, result, m = retrieve_page(url)
    if not status:
        return status, result, m
    urls = parse_page_snap(result)

    # Create directory to save the files
    create_dir(dir_name)

    # Download the files
    for source_file_url in urls:
        status, result, m = download_file(
            download_url.format(source_file_url), dir_name
        )
        if not status:
            return status, result, m
    return status, result, m


def find_deb_prefix(name):
    if name[0] != 'l' and name[0] in deb_lookup:
        return name[0]
    if name[0] == 'l':
        if len(name) >= 4:
            if name[:4] in deb_lookup_l:
                return name[:4]
        return 'l'
    return False


def parse_page_deb(page, source, version, prefix):
    """Parses a Debian deb HTML page and return URLs.
    """
    html = BeautifulSoup(page, 'html.parser')
    elements = [x.select('a')[0].get_text() for x in html.select('tr')[3:-1]]
    elements = list(filter(lambda x: not x.endswith("deb"), elements))
    sv = source + "_" + version + "."
    result = list(filter(lambda x: x.startswith(sv), elements))
    return [deb_url.format(prefix, source, x) for x in result]


def download_deb(source, version, dir_name):
    prefix = find_deb_prefix(source)
    if prefix is False:
        error_msg = {}
        m = 'find deb prefix'
        error_msg['phase'] = m
        error_msg['message'] = 'Source {}: error {}'.format(
            source, 'prefix not found'
        )
        return False, error_msg, m
    url = deb_url.format(
        prefix, source, ""
    )
    # Find urls
    status, result, m = retrieve_page(url)
    if not status:
        return status, result, m
    urls = parse_page_deb(result, source, version, prefix)

    # Create directory to save the files
    create_dir(dir_name)

    # Download the files
    for source_file_url in urls:
        status, result, m = download_file(source_file_url, dir_name)
        if not status:
            return status, result, m
    return status, result, m


def download(source, version, dir_name):
    """Download the debian source package file (.dsc) and the tar of project
    """
    status, result, m = download_snap(source, version, dir_name)
    status = False
    if status:
        return status, result, m
    status, result, m = download_deb(source, version, dir_name)
    return status, result, m


class PackageState():
    """A structure that contains the state for a package.
    """
    def __init__(self, record):
        self.record = record
        self.package = record['package']
        self.version = record['version']
        self.dist = record['release']
        self.source = record['source']
        self.sversion = record['source_version']
        self.dist = record['release']
        self.arch = record['arch']
        self.dir_name = '{}-{}-{}-{}'.format(
            self.source, self.dist, self.arch, self.sversion
        )
        self.callgraph_dir = '/{}/{}/{}/{}/{}/'.format(
            'callgraphs', self.source, self.dist, self.sversion, self.arch
        )
        self.source_dir = '/{}/{}/{}/{}/{}'.format(
            'sources', self.dist, self.source[0], self.source, self.sversion
        )
        self.dst = "sources/{}/{}/{}".format(
            self.source[0], self.source, self.sversion
        )
        self.urls = []
        self.profiling_data = {'times': {}}
        self.binary_pkgs = []
        self.old_cwd = os.getcwd()
        self.err = {'error': {'phase': '', 'message': '', 'crashed': False}}
        self.error_msg = self.err['error']
        self.status = ""

    def get_cg_dst(self, pkg):
        return "callgraphs/{}/{}/{}/{}/{}".format(
            pkg[0], pkg, self.dist, self.version, self.arch
        )


class CScoutKafkaPlugin(KafkaPlugin):
    """Produce C call graphs from Debian package releases.
    """
    def __init__(self, bootstrap_servers, consume_topic, produce_topic,
                 log_topic, error_topic, group_id, directory, debug):
        super().__init__(bootstrap_servers)
        self.consume_topic = consume_topic
        self.produce_topic = produce_topic
        self.log_topic = log_topic
        self.error_topic = error_topic
        self.group_id = group_id
        self.directory = directory
        self.debug = debug
        if not debug:
            self.set_consumer()
            self.set_producer()
        if debug:
            self.consume_topic = "consume_topic"
            self.produce_topic = "produce_topic"
            self.log_topic = "log_topic"
            self.error_topic = "error_topic"
            os.makedirs("debug", exist_ok=True)
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

    def download(self):
        """Download the source code of project
        """
        status, error, m = download(
            self.state.source, self.state.sversion, self.state.dir_name
        )
        if not status:
            self.log(m)
            self.state.error_msg['phase'] = error['phase']
            self.state.error_msg['message'] = error['message']
            self.state.error_msg['crashed'] = True
            raise PluginError("Error during downloading the dsc")

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
            self.state.error_msg['crashed'] = True
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
        if self.directory != '':
            self._copy_sources()
        if cmd.returncode == 1:
            message = 'Sbuild failed:\n{}'.format(stdout.decode(encoding='utf-8'))
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.state.error_msg['phase'] = 'run_sbuild'
            self.state.error_msg['message'] = message
            self.state.error_msg['crashed'] = True
            raise PluginError(message)
        os.chdir(self.state.old_cwd)

    def _copy_sources(self):
        try:
            if os.path.isdir(self.state.source_dir):
                dst = os.path.join(self.directory, self.state.dst)
                os.makedirs(dst, exist_ok=True)
                copy_tree(self.state.source_dir, dst)
                shutil.rmtree(self.state.source_dir)
        except:
            m = "{}: {} - {}.".format(
                str(datetime.datetime.now()),
                "Copy sources error",
                "Cannot copy {}".format(self.state.source_dir)
            )
            self.log(m)

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
                            self.state.error_msg['crashed'] = True
                            raise PluginError('Build failed')
                    elif log[0] == 'detect_binaries':
                        if log[1] == 'failed':
                            self.state.error_msg['phase'] = 'detect_binaries'
                            self.state.error_msg['message'] = 'No binaries found'
                            self.state.error_msg['crashed'] = True
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
                            self.state.error_msg['crashed'] = True
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
                            self._produce_cg_to_kafka(path, pkg)
        except FileNotFoundError:
            message = "File not found: " + self.state.callgraph_dir + "report"
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.log(m)
            self.state.error_msg['phase'] = 'report'
            self.state.error_msg['message'] = message
            self.state.error_msg['crashed'] = True
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

    def _produce_cg_to_kafka(self, path, pkg):
        """Push call graph to kafka topic and save it to disk.
        """
        try:
            with open(path + 'fcg.json', 'r') as f:
                call_graph = json.load(f)
            if self.directory != '':
                dst = os.path.join(self.directory, self.state.get_cg_dst(pkg))
                os.makedirs(dst, exist_ok=True)
                with open(os.path.join(dst, 'file.json'), 'w') as f:
                    json.dump(call_graph, f)
        except FileNotFoundError:
            message = "File not found: " + path + "fcg.json"
            m = "{}: {}".format(
                str(datetime.datetime.now()),
                message
            )
            self.log(m)
            self.state.error_msg['phase'] = 'read_fcg'
            self.state.error_msg['message'] = message
            self.state.error_msg['crashed'] = True
            raise PluginError(message)
        except:
            m = "{}: {} - {}.".format(
                str(datetime.datetime.now()),
                "Copy call graph error",
                "Cannot copy {}".format(self.state.get_cg_dst(pkg))
            )
            self.log(m)
        call_graph['profiling_data'] = self.state.profiling_data
        dst = os.path.join(self.directory, self.state.dst)
        call_graph['sourcePath'] = dst
        if self.directory != '':
            cg_dst = os.path.join(self.directory, self.state.get_cg_dst(pkg))
            cg_dst = os.path.join(cg_dst, "file.json")
            message = self.create_message(
                self.state.record, {"payload": {"dir": cg_dst}}
            )
        else:
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

    def emit_message(self, topic, msg, phase, log_msg):
        if self.debug:
            self.log("{}: Phase: {} Sent: {} to {}".format(
                str(datetime.datetime.now()), phase, log_msg, topic
            ))
            filename = "/home/builder/debug/" + topic + ".json"
            json.dump(msg, open(filename, 'a'))
            with open(filename, 'a') as f:
                f.write("\n")
        else:
            super().emit_message(topic, msg, phase, log_msg)


def get_parser():
    parser = argparse.ArgumentParser(
        "Consume Debian packages releases messages of a Kafka topic."
    )
    parser.add_argument(
        '-i',
        '--in-topic',
        type=str,
        help="Kafka topic to read from."
    )
    parser.add_argument(
        '-o',
        '--out-topic',
        type=str,
        help="Kafka topic to write to."
    )
    parser.add_argument(
        '-e',
        '--err-topic',
        type=str,
        help="Kafka topic to write errors to."
    )
    parser.add_argument(
        '-l',
        '--log-topic',
        type=str,
        help="Kafka topic to write logs to."
    )
    parser.add_argument(
        '-b',
        '--bootstrap-servers',
        type=str,
        help="Kafka servers, comma separated."
    )
    parser.add_argument(
        '-g',
        '--group',
        type=str,
        help="Kafka consumer group to which the consumer belongs."
    )
    parser.add_argument(
        '-s',
        '--sleep-time',
        type=int,
        default=60,
        help="Time to sleep in between each consuming (in sec)."
    )
    parser.add_argument(
        '-d',
        '--directory',
        type=str,
        default='',
        help="Path to base directory where sources will be saved."
    )
    parser.add_argument(
        '-D',
        '--debug',
        type=str,
        help="Debug mode, you should provide a JSON with a release."
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    in_topic = args.in_topic
    out_topic = args.out_topic
    err_topic = args.err_topic
    log_topic = args.log_topic
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time
    directory = args.directory
    debug = args.debug
    mandatory_args = (
        in_topic, out_topic, err_topic, log_topic, bootstrap_servers, group
    )

    # Handle options
    if (debug and any(x for x in mandatory_args)):
        message = "You cannot use any other argument with --debug option."
        raise parser.error(message)
    if (any(x for x in mandatory_args) and not all(x for x in mandatory_args)):
        message = "You should always use -i, -o, -e, -l, -b, and -g together."
        raise parser.error(message)

    plugin = CScoutKafkaPlugin(
        bootstrap_servers, in_topic, out_topic,
        log_topic, err_topic, group, directory, debug
    )

    if debug:
        record = ast.literal_eval(debug)
        plugin.consume(record)
    else:
        # Run forever
        while True:
            plugin.consume_messages()
            time.sleep(sleep_time)


def test_download():
    source = 'anna'
    version = '1.71'
    dir_name = 'anna_1.71'
    print(download(source, version, dir_name))
    source = 'h2o'
    version = '2.2.5+dfsg2-5'
    dir_name = 'h2o_2.2.5+dfsg2-5'
    print(download(source, version, dir_name))


if __name__ == "__main__":
    main()
    #  test_download()
