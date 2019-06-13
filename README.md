Dockerized Debian Builder
=========================

This repository contains various Dockerfiles that is needed to run [debian
builder](https://www.debian.org/devel/buildd/) in a single container.
Furthermore, it includes Dockerfiles for running program analysis tools
([SVF](https://github.com/SVF-tools/SVF),
[CSCout](https://github.com/dspinellis/cscout)),
as part of the [sbuild](https://wiki.debian.org/sbuild),
for producing call-graphs of C packages.


Images
======
* __wanna-build:__ An image with a tool that helps coordinate package building
through a Postgres database that keeps a list of packages and their status.
* __buildd:__ An image with a daemon that periodically checks the database
maintained by wanna-build and calls sbuild to build the packages.
* __svf:__ An image with LLVM toolchain, and SVF program analysis tool
installed, for producing call-graphs.
* __cscout:__ An image with CScout program analysis tool for producing
call-graphs.

Base Images
===========
* **wanna-build:** [official Postgres 9.6 image](
https://github.com/docker-library/postgres/tree/master/9.6).
* **buildd:** wanna-build
* **svf:** buildd
* **cscout:** buildd

Produce C call-graphs using SVF or CScout
=========================================
You need to have docker and docker-compose installed.

```bash
git clone git@github.com:fasten-project/debian-builder.git && cd debian-builder
./run-analysis.sh cscout # or svf
```

The produced call-graphs will be saved in the directory `./cscout/callgraphs`.
To stop and delete the container, change directory to the one with the
appropriate docker-compose.yml and run `docker-compose down -v`
