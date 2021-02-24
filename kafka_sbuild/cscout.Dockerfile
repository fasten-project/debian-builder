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
FROM schaliasos/sbuild-cscout:latest

RUN sudo apt -yqq update && sudo apt -yqq install libcurl4-openssl-dev libssl-dev
RUN pip3 install requests BeautifulSoup4 kafka-python fasten pycurl
RUN sudo pip3 install requests BeautifulSoup4 kafka-python fasten pycurl

# DIRECTORY TO SAVE DEBUG FILES
run mkdir -p /home/builder/debug
RUN chown -R builder /home/builder/debug
RUN chmod o+w /home/builder/debug/
# DIRECTORY TO SAVE DEBUG SOURCES
run mkdir -p /home/builder/debian
RUN chown -R builder /home/builder/debian
RUN chmod o+w /home/builder/debian/

COPY ./entrypoint.py entrypoint.py

ENTRYPOINT ["sudo", "python3", "entrypoint.py"]
