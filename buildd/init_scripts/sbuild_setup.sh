#! /bin/sh
set -e
sbuild-createchroot --include=eatmydata,ccache,gnupg stretch \
    /srv/chroot/stretch-amd64-sbuild http://deb.debian.org/debian && \
    sbuild-update -udcar stretch-amd64-sbuild
