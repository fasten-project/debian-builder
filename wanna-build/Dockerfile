FROM postgres:9.6

ENV build_deps="git vim wget"
ENV wanna_build_deps="libdbi-perl libyaml-libyaml-perl libhash-merge-perl libstring-format-perl libtimedate-perl libyaml-tiny-perl libdpkg-perl libdbd-pg-perl dctrl-tools moreutils dose-builddebcheck procmail dose-distcheck"
ENV RELEASE="stretch"
ENV ARCH="amd64"
ENV POS_VER="9.6"
ENV MIRROR="ftp.gr.debian.org"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade
RUN apt install -yqq $build_deps $wanna_build_deps

# DOWNLOAD WANNA-BUILD
RUN mkdir -p /srv
WORKDIR /srv
RUN git clone https://buildd.debian.org/git/wanna-build.git
RUN ln -s /srv/wanna-build/bin/wanna-build /usr/local/bin/wanna-build

# CHANGE DIRECTORY TO SCHEMA FOLDER
WORKDIR /srv/wanna-build/schema

# SET ARCHES
RUN sed -i "s/^ARCHES=.*/ARCHES=\"$ARCH\"/" arches-tables.sh
RUN ./arches-tables.sh

# ADD USER wbadm and create dir
RUN adduser --disabled-password --gecos ""  wbadm
RUN mkdir -p /srv/wanna-build/tmp
RUN chmod 760 /srv/wanna-build/tmp/
RUN chown wbadm. /srv/wanna-build/tmp/

# CONFIGURE postgres
RUN cp /usr/share/postgresql/$POS_VER/pg_service.conf.sample \
    /etc/postgresql-common/pg_service.conf
RUN echo "[wanna-build]\n" >> /etc/postgresql-common/pg_service.conf
RUN echo "dbname=wannadb\nuser=wbadm\n\n" >> \
    /etc/postgresql-common/pg_service.conf
RUN echo "[wanna-build-privileged]\n" >> /etc/postgresql-common/pg_service.conf
RUN echo "dbname=wannadb\nuser=wbadm\n" >> \
    /etc/postgresql-common/pg_service.conf
RUN mkdir -p /etc/postgresql/$POS_VER/main/
RUN cp /usr/share/postgresql/$POS_VER/pg_hba.conf.sample \
    /etc/postgresql/$POS_VER/main/pg_hba.conf
RUN sed -i '85ihost   all             wbadm                                   trust' \
    /etc/postgresql/$POS_VER/main/pg_hba.conf

# ADD "Packages-arch-specific"
RUN mkdir -p /srv/buildd.debian.org/web/quinn-diff/$RELEASE
WORKDIR /srv/buildd.debian.org/web/quinn-diff/$RELEASE/
RUN wget https://buildd.debian.org/quinn-diff/Packages-arch-specific

# ADD TRIGGER
COPY ./scripts/trigger.fasten /srv/wanna-build/triggers/trigger.fasten
RUN chmod a+x /srv/wanna-build/triggers/*
RUN touch /srv/wanna-build/logs/merge.local.log
RUN chmod a+rw /srv/wanna-build/logs/merge.local.log
RUN mkdir -p /srv/wanna-build/dumps
RUN chmod a+rw /srv/wanna-build/dumps

# DOWNLOAD Packages.gz AND Sources.gz
RUN mkdir -p /usr/archives/debian/dists/$RELEASE/main/source
RUN mkdir -p /usr/archives/debian/dists/$RELEASE/main/binary-$ARCH
WORKDIR /usr/archives/debian/dists/$RELEASE/main/source
RUN chmod a+rw /usr/archives/debian/dists/$RELEASE/main/source
RUN wget $MIRROR/debian/dists/$RELEASE/main/source/Sources.gz
RUN chmod a+rw /usr/archives/debian/dists/$RELEASE/main/source/Sources.gz
WORKDIR /usr/archives/debian/dists/$RELEASE/main/binary-$ARCH
RUN chmod a+rw /usr/archives/debian/dists/$RELEASE/main/binary-$ARCH
RUN wget $MIRROR/debian/dists/$RELEASE/main/binary-$ARCH/Packages.gz
RUN chmod a+rw /usr/archives/debian/dists/$RELEASE/main/binary-$ARCH/Packages.gz

# HACK TO RUN entrypoint SCRIPTS AS OTHER USER
# https://github.com/tianon/gosu/issues/11
RUN chown root:users /usr/local/bin/gosu
RUN chmod +s /usr/local/bin/gosu

# REPLACE docker-entrypoint.sh
RUN unlink /docker-entrypoint.sh
RUN rm /usr/local/bin/docker-entrypoint.sh
COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh /
