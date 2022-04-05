import asyncio
import datetime
import queue
import re
import threading
import time

import aiohttp

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

    async def check_url(self, url: str, search_pattern: str = "", rate=60):
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
                    self.responses_queue.put(turl_record)

                    toc = time.monotonic()
                    sleep_for = rate - (toc - tic)
                    await asyncio.sleep(sleep_for)

        self.ensure_exit()
        self.logger.info(f"closed tracking session for {url}")

    async def publish_url_checks(self):
        loop = asyncio.get_running_loop()
        self.producer = KafkaProducer(configs=self.config["kafka"], loop=loop)
        while True:
            items_to_process = self.responses_queue.qsize()
            if items_to_process == 0 and self.signal_exit.is_set():
                break
            self.logger.debug(
                f"waiting for event (queue size={self.responses_queue.qsize()})"
            )
            try:
                response = self.responses_queue.get(block=False)
                self.logger.debug(f"publishing: {response}")
                for topic in self.producer.topics:
                    await self.producer.produce(topic=topic, value=response.to_json())

            except queue.Empty:
                pass
            await asyncio.sleep(1)

        self.ensure_exit()
        self.logger.info("kafka publisher has terminated")

    def on_run(self):

        tasks = list()
        for host, host_conf in self.config["turl"]["hosts"].items():
            if host_conf is None:
                host_conf = dict()
            task = asyncio.create_task(self.check_url(url=host, **host_conf))
            tasks.append(task)

        tasks.append(asyncio.create_task(self.publish_url_checks()))
        return tasks

    def on_exit(self):
        self.producer.close()


def main():
    Turl().run()


if __name__ == "__main__":
    main()
