# Docker Images to produce C call graphs from Kafka

This Docker images get Debian packages releases events from a Kafka topic
and generates the corresponding call graphs using the either SVF or CScout
static analysis tools. The containers run indefinitely. They require the
options `--net=host`, and `--privileged`.

Build Images
------------

```bash
docker build -t kafka_svf -f svf.Dockerfile .
docker build -t kafka_cscout -f cscout.Dockerfile .
```

Dockerhub images
----------------

* svf: `schaliasos/kafka_svf:latest`
* cscout: ``

How to run
----------

```bash
usage: docker run -it --net=host --privileged schaliasos/kafka_svf
    in_topic out_topic err_topic bootstrap_servers group sleep_time [-h]

positional arguments:
  in_topic           Kafka topic to read from.
  out_topic          Kafka topic to write to.
  err_topic          Kafka topic to write errors to.
  bootstrap_servers  Kafka servers, comma separated.
  group              Kafka consumer group to which the consumer belongs.
  sleep_time         Time to sleep in between each scrape (in sec).

optional arguments:
  -h, --help         show this help message and exit
```

For example:

```bash
docker run -it --net=host --cap-add --privileged schaliasos/kafka_svf \
    cf_deb_release cf_fasten_cg cf_errors localhost:9092 group-1 60
```
