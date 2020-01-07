# Docker Image to produce C call graphs from Kafka

This Docker image gets Debian packages releases events from a Kafka topic
and generates the corresponding call graphs using the CScout static analysis
tool. The container runs indefinitely. It requires the options
`--net=host`, and `--cap-add SYS_ADMIN`.

How to run
----------

```bash
usage: docker run -it --net=host --cap-add SYS_ADMIN schaliasos/kafka_sbuild_cscout
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
docker run -it --net=host --cap-add SYS_ADMIN schaliasos/kafka_sbuild_cscout \
    cf_deb_release cf_fasten_cg cf_errors localhost:9092 group-1 60
```
