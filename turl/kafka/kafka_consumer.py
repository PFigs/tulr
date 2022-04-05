import asyncio
import json
import threading
import time

import confluent_kafka


class KafkaConsumer:
    def __init__(self, configs, message_queue, loop=None):
        self._loop = loop or asyncio.get_running_loop()
        self._cancelled = False
        self.config = configs
        self.topics = self.config["topics"]["consumer"]
        self._message_queue = message_queue
        self._consumer = confluent_kafka.Consumer(**self.config["consumer"])
        self._consumer.subscribe(self.topics)
        self._consumer_thread = None

    def start(self):
        self._consumer_thread = threading.Thread(target=self._consumer_loop)
        self._consumer_thread.start()

    def stop(self):
        self._cancelled = True

    def _consumer_loop(self):
        while not self._cancelled:
            messages = self._consumer.consume(timeout=1)
            for message in messages:
                if message.value() and not message.error():
                    msg = self.value_deserializer(message.value())
                    self._message_queue.put(msg)
                    time.sleep(0.1)

    @staticmethod
    def value_deserializer(value):
        """Called when a message is received to deserialize the message value"""
        try:
            value = json.loads(value)
        except (TypeError, json.decoder.JSONDecodeError):
            raise
        return value

    @staticmethod
    def key_deserializer(key):
        """Called when a message is received to deserialize the kafka key"""
        try:
            key = key.decode("utf-8")
        except (TypeError, AttributeError):
            raise
        return key
