# Docker Images to produce C call graphs from Kafka

This Docker images get Debian packages releases events from a Kafka topic
and generates the corresponding call graphs using the either SVF or CScout
static analysis tools. The containers run indefinitely. They require the
options `--net=host`, and `--privileged`.

Build Images
------------

```bash
docker build -t kafka-svf -f svf.Dockerfile .
docker build -t kafka-cscout -f cscout.Dockerfile .
```

Dockerhub images
----------------

* svf: `schaliasos/kafka_svf:latest`
* cscout: `schaliasos/kafka-cscout:latest`

How to run
----------

```bash
usage: Consume Debian packages releases messages of a Kafka topic. [-h] [-i IN_TOPIC] [-o OUT_TOPIC]
                                                                   [-e ERR_TOPIC] [-l LOG_TOPIC]
                                                                   [-b BOOTSTRAP_SERVERS] [-g GROUP]
                                                                   [-s SLEEP_TIME] [-d DIRECTORY]
                                                                   [-D DEBUG]

optional arguments:
  -h, --help            show this help message and exit
  -i IN_TOPIC, --in-topic IN_TOPIC
                        Kafka topic to read from.
  -o OUT_TOPIC, --out-topic OUT_TOPIC
                        Kafka topic to write to.
  -e ERR_TOPIC, --err-topic ERR_TOPIC
                        Kafka topic to write errors to.
  -l LOG_TOPIC, --log-topic LOG_TOPIC
                        Kafka topic to write logs to.
  -b BOOTSTRAP_SERVERS, --bootstrap-servers BOOTSTRAP_SERVERS
                        Kafka servers, comma separated.
  -g GROUP, --group GROUP
                        Kafka consumer group to which the consumer belongs.
  -s SLEEP_TIME, --sleep-time SLEEP_TIME
                        Time to sleep in between each consuming (in sec).
  -d DIRECTORY, --directory DIRECTORY
                        Path to base directory where sources will be saved.
  -D DEBUG, --debug DEBUG
                        Debug mode, you should provide a JSON with a release.
```

For example:

```bash
docker run -it --net=host --privileged schaliasos/kafka_svf \
    -i cf_deb_release -o cf_fasten_cg -e cf_errors -l cf_logs -b localhost:9092 -g group-1 -s 60
```

Debug Example
-------------

```bash
sudo docker run -it --privileged \
    -v $(pwd)/temp/debug:/home/builder/debug \
    -v $(pwd)/temp/debian:/mnt/fasten/debian \
    kafka-cscout --directory /mnt/fasten/debian \
    --debug "{'source': 'anna', 'version': '1.71', 'arch': 'amd64', 'release': 'buster',  'date': ''}"
```
