# vim:set ft=dockerfile:
FROM schaliasos/sbuild:latest

WORKDIR /root

# INSTALL CScout
RUN git clone https://github.com/dspinellis/cscout/
WORKDIR cscout
COPY ./csc_src/* src/
RUN make && make install

WORKDIR /root

# INSTALL fcan
RUN wget https://raw.githubusercontent.com/fasten-project/canonical-call-graph-generator/master/fcan/fcan/fcan.py && \
    cp fcan.py /usr/local/bin/fcan && chmod +x /usr/local/bin/fcan

WORKDIR /root

# SCRIPT TO RUN TOOLS
COPY ./scripts/analyzer_cscout /usr/local/bin/analyzer
COPY ./scripts/wrapper_analyzer /usr/local/bin/wrapper_analyzer
RUN chmod 777 /usr/local/bin/analyzer 77 \
    chmod 777 /usr/local/bin/wrapper_analyzer

# DIRECTORY TO SAVE CALL-GRAPHS
RUN mkdir -p /var/log/sbuild/callgraphs && mkdir -p /var/log/sbuild/stats

COPY ./config/sbuildrc /root/.sbuildrc
COPY ./config/fstab /etc/schroot/sbuild/fstab
