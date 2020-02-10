# vim:set ft=dockerfile:
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

USER builder
WORKDIR /home/builder
