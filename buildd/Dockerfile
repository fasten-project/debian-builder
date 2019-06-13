FROM wanna-build

ENV build_deps="git make vim wget python python-pip cmake g++ sudo cron"
ENV sbuild_buildd="sbuild buildd schroot debootstrap openssh-server"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade
RUN apt install -yqq $build_deps $sbuild_buildd

# INSTALL perl PACKAGE
RUN echo -e "\n\n" | cpan URI:Escape

# INSTALL sbuild
RUN sbuild-adduser buildd

WORKDIR /root

# Set cron job to restart buildd when buildd failed
COPY ./scripts/check_buildd.sh /usr/local/bin/check_buildd
RUN chmod 777 /usr/local/bin/check_buildd
COPY ./scripts/check-buildd-cron /etc/cron.d/check-buildd-cron
RUN chmod 0644 /etc/cron.d/check-buildd-cron
RUN crontab /etc/cron.d/check-buildd-cron

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
