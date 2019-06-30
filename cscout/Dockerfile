FROM buildd

ENV build_deps="git make vim wget python python-pip cmake g++ sudo cron"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade
RUN apt install -yqq $build_deps

WORKDIR /root

# INSTALL CScout
RUN git clone https://github.com/dspinellis/cscout/
WORKDIR cscout
COPY ./csc_src/* src/
RUN make && make install

WORKDIR /root

# SCRIPT TO RUN TOOLS
COPY ./scripts/analyzer_cscout /usr/local/bin/analyzer
RUN chmod 777 /usr/local/bin/analyzer

# DIRECTORY TO SAVE CALL-GRAPHS
RUN mkdir -p /var/lib/buildd/callgraphs

# CONFIG FILES
COPY ./config/sbuildrc /var/lib/buildd/.sbuildrc
COPY ./config/buildd.conf ./
COPY ./patches/Daemon.patch ./
COPY ./config/fstab /etc/schroot/sbuild/fstab

# REPLACE docker-entrypoint.sh
RUN unlink /docker-entrypoint.sh
RUN rm /usr/local/bin/docker-entrypoint.sh
COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh /
