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

WORKDIR /root

# INSTALL CScout
RUN git clone https://github.com/dspinellis/cscout.git
WORKDIR cscout
RUN make && make install

WORKDIR /root

# INSTALL fcan
RUN wget https://raw.githubusercontent.com/fasten-project/canonical-call-graph-generator/master/fcan/fcan/fcan.py && \
    cp fcan.py /usr/local/bin/fcan && chmod +x /usr/local/bin/fcan

WORKDIR /root

# SCRIPT TO RUN TOOLS
COPY ./scripts/base_analyzer /usr/local/bin/base_analyzer
COPY ./scripts/cscout/analyzer /usr/local/bin/analyzer

# CONFIG FILES
COPY ./config/cscout/sbuildrc /root/.sbuildrc
COPY ./config/cscout/sbuildrc /home/builder/.sbuildrc
COPY ./config/cscout/fstab /etc/schroot/sbuild/fstab

# DIRECTORY TO SAVE CALL-GRAPHS
run mkdir -p /callgraphs
RUN chown -R builder /callgraphs
RUN chmod o+w /callgraphs/
# DIRECTORY TO SAVE SOURCES
run mkdir -p /sources
RUN chown -R builder /sources
RUN chmod o+w /sources/

USER builder
WORKDIR /home/builder
