import asyncio
import datetime
import queue
import re
import threading
import time

import aiohttp
import confluent_kafka

from .aiobase import AioBase
from .configuration import Configuration
from .kafka import KafkaProducer
from .turl_record import TurlRecord


class Turl(AioBase):
    def __init__(self, config_filepath=None, logger=None):
        self.config = Configuration(filepath=config_filepath).fetch_from_file()
        super().__init__(level=self.config["logger"]["level"], logger=logger)
        self.responses_queue = queue.Queue(maxsize=1000)
        self.signal_exit = threading.Event()
        self.producer = None

    async def check_url(
        self, url: str, search_pattern: str = "", rate=60, topic="turl"
    ):
        has_content = False
        async with aiohttp.ClientSession() as session:
            while not self.signal_exit.is_set():
                ts = datetime.datetime.utcnow()
                tic = time.monotonic()
                async with session.get(url) as response:
                    toc = time.monotonic()
                    elapsed = toc - tic

                    if search_pattern:
                        page_content = await response.text()
                        has_content = bool(re.search(search_pattern, page_content))

                    turl_record = TurlRecord(
                        url=url,
                        status_code=response.status,
                        elapsed=elapsed,
                        content_search_pattern=search_pattern,
                        content_search_success=has_content,
                        last_check=ts.isoformat(),
                    )

                    try:
                        await self.publish_url_checks(
                            topic=topic, message=turl_record.to_json()
                        )
                    except confluent_kafka.error.ProduceError as error:
                        self.logger.error(error)
                        self.signal_exit.set()
                        break

                    toc = time.monotonic()
                    sleep_for = rate - (toc - tic)
                    await asyncio.sleep(sleep_for)

        self.ensure_exit()
        self.logger.info(f"closed tracking session for {url}")

    async def publish_url_checks(self, topic, message):
        self.logger.debug(f"publishing: {message} to {topic}")
        try:
            await self.producer.produce(topic=topic, value=message)
        except confluent_kafka.KafkaException:
            if not self.signal_exit.is_set():
                self.signal_exit.set()

    def on_error_cb(self, error: confluent_kafka.error.KafkaError):
        self.logger.error(error)
        if not self.signal_exit.is_set():
            self.signal_exit.set()

    def on_delivery_cb(self, error: confluent_kafka.error.KafkaError):
        self.logger.error(error)
        if not self.signal_exit.is_set():
            self.signal_exit.set()

    def on_run(self):

        tasks = list()
        loop = asyncio.get_running_loop()

        self.config["kafka"]["producer"]["error_cb"] = self.on_error_cb

        try:
            self.producer = KafkaProducer(
                configs=self.config["kafka"], loop=loop, logger=self.logger
            )
        except confluent_kafka.KafkaException as error:
            self.logger.error(error)
            return

        for host, host_conf in self.config["turl"]["hosts"].items():
            if host_conf is None:
                host_conf = dict()
            task = asyncio.create_task(self.check_url(url=host, **host_conf))
            tasks.append(task)

        return tasks

    def on_exit(self):
        self.producer.close()


def main():
    Turl().run()


if __name__ == "__main__":
    main()
