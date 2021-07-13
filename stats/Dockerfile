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
FROM debian:stable

ENV dev="vim wget sudo pkg-config ctags"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade && apt install -yqq $dev

# Add user to run sbuild
RUN useradd -ms /bin/bash user && echo "user:user" | chpasswd && adduser user sudo
RUN echo "%sudo  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER user

WORKDIR /home/user

ADD ./entrypoint.sh /home/user
ENTRYPOINT ["./entrypoint.sh"]
