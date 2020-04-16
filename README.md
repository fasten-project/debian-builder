Dockerized Debian Infrastructure to Analyze Packages
====================================================

This repository contains various Dockerfiles and scripts that can be used to
analyze Debian packages.
Specifically, it includes Dockerfiles for running program analysis tools
([SVF](https://github.com/SVF-tools/SVF),
[CSCout](https://github.com/dspinellis/cscout)),
as part of the [sbuild](https://wiki.debian.org/sbuild),
for producing call-graphs of C packages.
It also provides enhanced docker images to use them with Kafka.


Images
======
* __sbuild:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/sbuild/Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/sbuild)
* __sbuild-svf:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/sbuild/svf.Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/sbuild) **Broken**
* __sbuild-cscout:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/sbuild/cscout.Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/sbuild)
* __sbuild-dynamic:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/sbuild/dynamic.Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/sbuild)
* __kafka-svf:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/kafka_sbuild/svf.Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/kafka_sbuild) **Broken**
* __kafka-cscout:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/kafka_sbuild/cscout.Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/kafka_sbuild)
* __kafka-filter-debian:__ [Dockerfile](https://github.com/fasten-project/debian-builder/blob/master/kafka_filter_debian/Dockerfile), [Instructions](https://github.com/fasten-project/debian-builder/tree/master/kafka_filter_debian)
