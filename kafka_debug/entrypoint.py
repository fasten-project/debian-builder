import os
import json
import argparse
import datetime
import random
from kafka import KafkaProducer
from kafka import KafkaConsumer


TOPIC_CG = "fasten.debian.cg.test.1"
TOPIC_ERR = "fasten.debian.cg_errors.test.1"
TOPIC_LOG = "fasten.debian.log.test.1"
SERVERS = "samos:9092,delft:9092,goteborg:9092"
GROUP = "foo1"

def fetch(topic, servers, group, timeout=10000):
    # Create consumer
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=servers.split(','),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=timeout
    )
    messages = []
    for message in consumer:
        m = message.value
        messages.append(m)
    return messages


def get_messages(timeout=10000):
    group = GROUP + str(random.getrandbits(128))
    cg = fetch(TOPIC_CG, SERVERS, group, timeout)
    err = fetch(TOPIC_ERR, SERVERS, group, timeout)
    log = fetch(TOPIC_LOG, SERVERS, group, timeout)
    return cg, err, log


def get_sources(messages):
    return [i['source'] for i in messages]


def get_packages(messages):
    return [i['product'] for i in messages]


def get_failed(cg, errors):
    sources = {i['source'] for i in cg}
    errors = {i['source'] for i in errors}
    return errors - sources


def get_error_stats(messages):
    stats = {'phase': {}, 'type': {}}
    for err in messages:
        phase = err['error']['phase']
        etype = err['error']['type']
        if phase in stats['phase']:
            stats['phase'][phase] += 1
        else:
            stats['phase'][phase] = 1
        if etype in stats['type']:
            stats['type'][etype] += 1
        else:
            stats['type'][etype] = 1
    return stats


def uncomplete(messages):
    packages = set()
    for log in messages:
        if log['phase'] == 'begin':
            packages.add(log['package'])
        elif log['phase'] == 'complete' or log['phase'] == 'failed':
            packages.discard(log['package'])
    return packages


def get_parser():
    parser = argparse.ArgumentParser(
        "Debug Kafka topics"
    )
    parser.add_argument('topic', type=str, help="Kafka topic to read from.")
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
    return parser
