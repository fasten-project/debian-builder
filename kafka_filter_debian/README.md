# Docker Image to filter releases of Debian Packages from Kafka

This Docker image gets Debian packages releases events from a Kafka topic,
filter them to keep only unique sources, and push them to another Kafka topic.
The container runs indefinitely. It requires the options
`--net=host`.

How to run
----------

```bash
usage: docker run -it --net=host schaliasos/kafka_filter_debian
    in_topic out_topic bootstrap_servers group sleep_time -f FILENAME [-h]

positional arguments:
  in_topic           Kafka topic to read from.
  out_topic          Kafka topic to write to.
  bootstrap_servers  Kafka servers, comma separated.
  group              Kafka consumer group to which the consumer belongs.
  sleep_time         Time to sleep in between each scrape (in sec).

optional arguments:
  -h, --help         show this help message and exit
  -f, --filename     File to save the sources
```

For example:

```bash
docker run -it --net=host schaliasos/kafka_filter_debian \
    -v /local/path/sources.json:/root/sources.json
    cf_deb_release cf_fasten_cg localhost:9092 group-1 60 -f sources.json
```
