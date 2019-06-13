#! /bin/sh
cd ~ && \
ssh-keygen -N '' -f /var/lib/buildd/.ssh/id_rsa  && \
cd /var/lib/buildd/.ssh/ && cat id_rsa.pub > authorized_keys && \
ssh-keyscan -H 127.0.0.1 >> ~/.ssh/known_hosts
