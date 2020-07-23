import os
import time
import json
import argparse
import datetime
from kafka import KafkaProducer
from kafka import KafkaConsumer


def parse_release(release):
    source = release['source']
    version = release['source_version']
    dist = release['release']
    arch = release['arch']
    return source, version, dist, arch


def filter_sources(sources, release):
    """Check if a source has already been consumed. If has not then add it to
    sources dict.
    """
    source, version, dist, arch = parse_release(release)
    if source not in sources.keys():
        sources[source] = {version: {dist: [arch]}}
        return True
    elif version not in sources[source].keys():
        sources[source][version] = {dist: [arch]}
        return True
    elif dist not in sources[source][version]:
        sources[source][version][dist] = [arch]
        return True
    elif arch not in sources[source][version][dist]:
        sources[source][version][dist].append(arch)
        return True
    return False


def run(in_topic, out_topic, servers, group, filename, sources={},
        check_old=False):
    """Consume from a kafka topic metadata of source, filter them in order not
       to consume twice the same source, push the sources in another topic.
    """
    # Create consumer
    consumer = KafkaConsumer(
        in_topic,
        bootstrap_servers=servers.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    # Create consumer for output topic to get all the old messages
    if check_old:
        consumer_old = KafkaConsumer(
            out_topic,
            bootstrap_servers=servers.split(','),
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        for message in consumer_old:
            release = message.value
            filter_sources(sources, release)
    # Create producer
    producer = KafkaProducer(
        bootstrap_servers=servers.split(','),
        value_serializer=lambda x: x.encode('utf-8')
    )

    # Read messages
    for message in consumer:
        release = message.value
        print("{}: Consuming {}".format(
            str(datetime.datetime.now()), release)
        )
        # Check if source is in sources
        if filter_sources(sources, release):
            # Push release to topic
            producer.send(out_topic, json.dumps(release))
            # Save sources
            if filename:
                with open(filename, 'w') as f:
                    json.dump(sources, f)
    return sources


def get_parser():
    parser = argparse.ArgumentParser(
        "Filter Debian packages releases messages of a Kafka topic."
    )
    parser.add_argument('in_topic', type=str, help="Kafka topic to read from.")
    parser.add_argument(
        'out_topic',
        type=str,
        help="Kafka topic to write to."
    )
    parser.add_argument(
        'bootstrap_servers',
        type=str,
        help="Kafka servers, comma separated."
    )
    parser.add_argument(
        'group',
        type=str,
        help="Kafka consumer group to which the consumer belongs."
    )
    parser.add_argument(
        'sleep_time',
        type=int,
        help="Time to sleep."
    )
    parser.add_argument(
        '-f',
        '--filename',
        dest='filename',
        help="File to save sources metadata.",
        default='sources.json'
    )
    parser.add_argument(
        '-o',
        '--check-old',
        dest='check_old',
        action='store_true',
        help="Read messages from output topic before start",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    in_topic = args.in_topic
    out_topic = args.out_topic
    bootstrap_servers = args.bootstrap_servers
    group = args.group
    sleep_time = args.sleep_time
    filename = args.filename if args.filename else False
    check_old = args.check_old

    # Read the sources that has been already consumed
    sources = {}
    if filename:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                sources = json.load(f)

    # Run forever
    while True:
        sources = run(
            in_topic, out_topic, bootstrap_servers, group,
            filename, sources, check_old
        )
        check_old = False
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()
