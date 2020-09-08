# vim:set ft=dockerfile:
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
FROM schaliasos/sbuild:latest

USER root

ENV deps="graphviz libgraphviz-dev valgrind binutils python3 python3-pip"
ENV pip_deps="networkx pydot gprof2dot setuptools pygraphviz"

RUN apt -yqq update && apt -yqq upgrade && apt install -yqq $deps
RUN pip3 install setuptools pygraphviz networkx

WORKDIR /root

# SCRIPT TO RUN TOOLS
COPY ./scripts/base_analyzer /usr/local/bin/base_analyzer
COPY ./scripts/dynamic/analyzer /usr/local/bin/analyzer
COPY ./scripts/dynamic/dot2csv /usr/local/bin/dot2csv

# CONFIG FILES
COPY ./config/dynamic/sbuildrc /root/.sbuildrc
COPY ./config/dynamic/sbuildrc /home/builder/.sbuildrc
COPY ./config/dynamic/fstab /etc/schroot/sbuild/fstab

# DIRECTORY TO SAVE CALL-GRAPHS
run mkdir -p /callgraphs
RUN chown -R builder /callgraphs
RUN chmod o+w /callgraphs/

USER builder
WORKDIR /home/builder
