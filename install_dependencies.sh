#! /bin/sh
#
# Install docker and docker-compose to a Debian stable machine.
# (Run this script as root)
#
apt update -yqq && apt upgrade -yqq
apt install -yqq apt-transport-https ca-certificates curl \
    software-properties-common gnupg2
# Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt update -yqq
apt install -yqq docker-ce
# Compose
curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
