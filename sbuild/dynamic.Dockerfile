# vim:set ft=dockerfile:
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
