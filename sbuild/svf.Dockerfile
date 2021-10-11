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

ENV build_deps="wget python python-pip cmake g++"
ENV svf_deps="zlib1g-dev libncurses5-dev libssl-dev libpcre2-dev zip"
ENV llvm_deps="libllvm-7-ocaml-dev libllvm7 llvm-7 llvm-7-dev llvm-7-doc llvm-7-examples llvm-7-runtime"
ENV clang_deps="clang-7 clang-tools-7 clang-7-doc libclang-common-7-dev libclang-7-dev libclang1-7 clang-format-7 python-clang-7"
ENV llvm_linker_etc="libfuzzer-7-dev lldb-7 lld-7 libc++-7-dev libc++abi-7-dev libomp-7-dev"
ENV python_deps="python3 python3-pip python3-dev graphviz-dev"

# INSTALL PACKAGES
COPY sources.list /etc/apt/sources.list

RUN apt -yqq update && apt -yqq upgrade && \
    apt install -yqq $build_deps $svf_deps $llvm_deps $clang_deps $llvm_linker_etc $python_deps

# Pip packages to install
RUN pip3 install setuptools pygraphviz networkx

WORKDIR /root

# INSTALL SVF
ENV LLVM_SRC=/usr/local/installations/llvm-7.0.0.src
ENV LLVM_OBJ=/usr/lib/llvm-7/build
ENV LLVM_DIR=/usr/lib/llvm-7/build
RUN mkdir -p /usr/local/installations
WORKDIR /usr/local/installations
RUN wget http://llvm.org/releases/7.0.0/llvm-7.0.0.src.tar.xz && \
    tar xf llvm-7.0.0.src.tar.xz && \
    git clone https://github.com/SVF-tools/SVF.git SVF
WORKDIR SVF
RUN mkdir Release-build
WORKDIR Release-build
RUN cmake ../ && make -j4
ENV SVF_HOME=/usr/local/installations/SVF/
ENV PATH=$SVF_HOME/Release-build/bin:$PATH
RUN pip install wllvm

WORKDIR /root

# Install llvm-func-info
RUN git clone https://github.com/fasten-project/llvm-func-info.git
WORKDIR llvm-func-info/DumpFuncInfo
RUN mkdir build
WORKDIR build
RUN cmake -DLLVM_BUILD_DIR=/usr/lib/llvm-7/build ..
RUN make
RUN sudo install FuncInfoPass/libLLVMFuncInfoPass.so /usr/local/bin/
WORKDIR ../../
RUN sudo install scripts/extract-edgelist.py /usr/local/bin/
RUN sudo install scripts/extract-function-info.sh /usr/local/bin/

WORKDIR /root

# Install fcan
RUN wget https://raw.githubusercontent.com/fasten-project/canonical-call-graph-generator/master/fcan/fcan/fcan.py && \
    cp fcan.py /usr/local/bin/fcan && chmod +x /usr/local/bin/fcan

# SCRIPT TO RUN TOOLS
COPY ./scripts/base_analyzer /usr/local/bin/base_analyzer
COPY ./scripts/svf/analyzer /usr/local/bin/analyzer

# CONFIG FILES
COPY ./config/svf/sbuildrc /root/.sbuildrc
COPY ./config/svf/sbuildrc /home/builder/.sbuildrc
COPY ./config/svf/fstab /etc/schroot/sbuild/fstab

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
