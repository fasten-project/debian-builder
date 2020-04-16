#! /bin/bash
cd sbuild
docker build -t sbuild -f Dockerfile .
docker tag sbuild schaliasos/sbuild
docker build -t sbuild-cscout -f cscout.Dockerfile .
docker tag sbuild-cscout schaliasos/sbuild-cscout
# docker build -t sbuild-svf -f svf.Dockerfile .
# docker tag sbuild-svf schaliasos/sbuild-svf
docker build -t sbuild-dynamic -f dynamic.Dockerfile .
docker tag sbuild-dynamic schaliasos/sbuild-dynamic
cd ../kafka_sbuild
docker build -t kafka-sbuild -f Dockerfile .
docker tag kafka-sbuild schaliasos/kafka-sbuild
docker build -t kafka-cscout -f cscout.Dockerfile .
docker tag kafka-cscout schaliasos/kafka-cscout
# docker build -t kafka-svf -f svf.Dockerfile .
# docker tag kafka-svf schaliasos/kafka-svf
cd ../kafka_filter_debian
docker build -t kafka-filter-debian -f Dockerfile .
docker tag kafka-filter-debian schaliasos/kafka-filter-debian
