#! /bin/bash
cd sbuild
sudo docker build -t sbuild -f Dockerfile .
sudo docker tag sbuild schaliasos/sbuild
sudo docker build -t sbuild-cscout -f cscout.Dockerfile .
sudo docker tag sbuild-cscout schaliasos/sbuild-cscout
sudo docker build -t sbuild-svf -f svf.Dockerfile .
sudo docker tag sbuild-svf schaliasos/sbuild-svf
cd ../kafka_sbuild
sudo docker build -t kafka-sbuild -f Dockerfile .
sudo docker tag kafka-sbuild schaliasos/kafka-sbuild
sudo docker build -t kafka-cscout -f cscout.Dockerfile .
sudo docker tag kafka-cscout schaliasos/kafka-cscout
sudo docker build -t kafka-svf -f svf.Dockerfile .
sudo docker tag kafka-svf schaliasos/kafka-svf
cd ../kafka_filter_debian
sudo docker build -t kafka-filter-debian -f Dockerfile .
sudo docker tag kafka-filter-debian schaliasos/kafka-filter-debian
