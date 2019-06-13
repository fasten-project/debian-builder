#! /bin/sh
set -e
usermod -a -G sbuild buildd
touch /var/log/buildd.log
chown buildd:buildd /var/log/buildd.log
cp /root/buildd.conf /etc/buildd/buildd.conf
patch /usr/share/perl5/Buildd/Daemon.pm < /root/Daemon.patch
