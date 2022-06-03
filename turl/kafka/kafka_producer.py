import asyncio
import threading

import confluent_kafka
from confluent_kafka import KafkaException


class KafkaProducer:
    """
    Based on
    https://www.confluent.io/blog/kafka-python-asyncio-integration/
    https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/asyncio_example.py
    """

    def __init__(self, configs, loop=None, logger=None):
        self._loop = loop or asyncio.get_running_loop()
        self.config = configs
        self._producer = confluent_kafka.Producer(
            **self.config["producer"], logger=logger
        )
        self._cancelled = False
        self._poll_thread = threading.Thread(target=self._poll_loop)
        self._poll_thread.start()
        self.topics = self.config["topics"]["producer"]

    def error_cb(self, error):
        print(error)

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value):
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err)
                )
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)

        self._producer.produce(topic, value, on_delivery=ack)
        return result
