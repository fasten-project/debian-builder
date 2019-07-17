# vim:set ft=dockerfile:
FROM debian:stable

ENV dev="git make vim wget python python-pip cmake g++ sudo python3 python3-pip"
ENV sbuild="sbuild schroot debootstrap"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade
RUN apt install -yqq $dev $sbuild

# INSTALL sbuild
RUN sbuild-adduser root
RUN sbuild-createchroot --include=eatmydata,ccache,gnupg unstable /srv/chroot/unstable-amd64-sbuild http://deb.debian.org/debian
RUN sbuild-createchroot --include=eatmydata,ccache,gnupg stretch /srv/chroot/stretch-amd64-sbuild http://deb.debian.org/debian

WORKDIR /root

# DIRECTORY TO SAVE STATS
RUN mkdir -p /var/lib/fasten/stats

COPY ./config/sbuildrc /root/.sbuildrc
COPY ./config/fstab /etc/schroot/sbuild/fstab
