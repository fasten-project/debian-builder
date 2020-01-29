#! /bin/bash
cd sbuild
sudo docker build -t sbuild -f Dockerfile .
sudo docker tag sbuild schaliasos/sbuild
sudo docker build -t sbuild_cscout -f cscout.Dockerfile .
sudo docker tag sbuild_cscout schaliasos/sbuild_cscout
sudo docker build -t sbuild_svf -f svf.Dockerfile .
sudo docker tag sbuild_svf schaliasos/sbuild_svf
cd ../kafka_sbuild
sudo docker build -t kafka_sbuild -f Dockerfile .
sudo docker tag kafka_sbuild schaliasos/kafka_sbuild 
sudo docker build -t kafka_cscout -f cscout.Dockerfile .
sudo docker tag kafka_cscout schaliasos/kafka_cscout 
sudo docker build -t kafka_svf -f svf.Dockerfile .
sudo docker tag kafka_svf schaliasos/kafka_svf 
