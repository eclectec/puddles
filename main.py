from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer
from os import getenv
import logging
import redis
import time

message_broker = getenv("BROKER", "kafka")
broker_port = getenv("PORT", "9093")
topics = getenv("TOPIC", "rumble")

def subscribe_to_redis_topics():
    client = redis.Redis(host="redis", port=broker_port, db=0)
    consumer = client.pubsub()
    for topic in topics.split(","):
        consumer.subscribe(topic)

    for message in consumer.listen():
        logging.warning(f'''Received message: {message}''')


def subscribe_to_kafka_topics():
    consumer = Consumer({
        'bootstrap.servers': f'''kafka:{broker_port}''',
        'group.id': 'turbine',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(topics.split(","))
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            logging.error("Consumer error: {}".format(msg.error()))
            continue

        logging.warning("Received message: {}".format(msg.value().decode("utf-8")))

    consumer.close()

def main():
    time.sleep(30)

    if(message_broker == "kafka"):
        subscribe_to_kafka_topics()
    else:
        subscribe_to_redis_topics()
            

if __name__ == "__main__":
    main()
