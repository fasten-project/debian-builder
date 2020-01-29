# vim:set ft=dockerfile:
FROM debian:stable

ENV dev="git make vim wget python3 python3-pip sudo"
ENV sbuild="sbuild schroot debootstrap"

# INSTALL PACKAGES
RUN apt -yqq update && apt -yqq upgrade && apt install -yqq $dev $sbuild

# Add user to run sbuild
RUN useradd -ms /bin/bash builder && echo "builder:builder" | chpasswd && adduser builder sudo
RUN echo "%sudo  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# INSTALL sbuild
RUN sbuild-adduser root && \
    sbuild-adduser builder && \
    sbuild-createchroot --include=eatmydata,ccache,gnupg stable /srv/chroot/stable-amd64-sbuild http://deb.debian.org/debian && \
    sbuild-createchroot --include=eatmydata,ccache,gnupg buster /srv/chroot/buster-amd64-sbuild http://deb.debian.org/debian && \
    sbuild-createchroot --include=eatmydata,ccache,gnupg stretch /srv/chroot/stretch-amd64-sbuild http://deb.debian.org/debian

# DIRECTORY TO SAVE STATS
RUN mkdir -p /var/log/sbuild/stats
RUN chown -R builder /var/log/sbuild

COPY ./config/sbuildrc /root/.sbuildrc
COPY ./config/fstab /etc/schroot/sbuild/fstab

USER builder

COPY ./config/sbuildrc /home/builder/.sbuildrc

WORKDIR /home/builder
