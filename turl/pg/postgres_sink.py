import asyncio
import queue
import threading

import aiopg
import psycopg2
import schema
from schema import And, Or, Optional

from ..aiobase import AioBase
from ..configuration import Configuration, is_uuid, is_url, is_valid_http_code
from ..kafka import KafkaConsumer


class PgSink(AioBase):
    record_schema = {
        "1.0": {
            "record_id": is_uuid,
            "host_id": is_uuid,
            "url": is_url,
            "response_time": And(lambda x: x > 0, Or(int, float)),
            "status_code": is_valid_http_code,
            "last_check": str,
            Optional("content_search_pattern"): Or(str, None),
            Optional("content_search_success"): Or(bool, None),
        }
    }

    def __init__(self, config_filepath=None, logger=None):
        self.config = Configuration(filepath=config_filepath).fetch_from_file()
        super().__init__(level=self.config["logger"]["level"], logger=logger)
        self.records_queue = queue.Queue(maxsize=1000)
        self.signal_exit = threading.Event()
        self._consumer = None
        self.wait_for_writer = threading.Event()

    async def write_record(self, pg_cursor, record):
        try:
            record_schema = self.record_schema[str(record["version"])]
            validated_record = schema.Schema(
                record_schema, ignore_extra_keys=True
            ).validate(record)
        except KeyError as error:
            self.logger.error(
                f"unable to write response due to unsupported version {record['version']} vs {error} - supports {self.record_schema.keys()}"
            )
            return
        except schema.SchemaMissingKeyError as error:
            self.logger.error(f"unable to write response due to missing key - {error}")
            return
        record_keys = list(validated_record.keys())
        records_to_write = ", ".join([f'"{key}"' for key in record_keys])
        values_to_write = tuple([validated_record[key] for key in record_keys])
        values_insert_string = ",%s" * len(record_keys)
        insert_clause = f'INSERT INTO "records" ({records_to_write}) VALUES ( {values_insert_string[1:]} )'
        try:
            await pg_cursor.execute(insert_clause, values_to_write)
        except psycopg2.errors.UniqueViolation as error:
            self.logger.error(error)

    async def writer(self):
        dsn = " ".join([f"{k}={v}" for k, v in self.config["pg"].items()])
        self.logger.info(f"starting writer towards host={self.config['pg']['host']}")
        try:
            async with aiopg.create_pool(dsn) as pool:
                self.logger.debug("created pool")
                async with pool.acquire() as pg_connection:
                    self.logger.debug("acquired connection pool")
                    async with pg_connection.cursor() as pg_cursor:
                        self.logger.debug("acquired cursor")
                        self.wait_for_writer.set()

                        while True:
                            items_to_process = self.records_queue.qsize()
                            if items_to_process == 0 and self.signal_exit.is_set():
                                break
                            try:
                                record = self.records_queue.get(block=False)
                                self.logger.debug(f"writing record {record}")
                                await self.write_record(pg_cursor, record)
                            except queue.Empty:
                                pass
                            await asyncio.sleep(0.1)
        except psycopg2.OperationalError as error:
            self.logger.info(error)
        except asyncio.exceptions.TimeoutError:
            self.logger.info("Could not reach pg host")

        self.ensure_exit()
        self.wait_for_writer.set()

        self.logger.info("writer has terminated")

    async def consumer(self):
        self._consumer = KafkaConsumer(
            self.config["kafka"], message_queue=self.records_queue
        )
        while not self.wait_for_writer.is_set():
            await asyncio.sleep(1)

        self.logger.info("starting consumer")
        self._consumer.start()
        while not self.signal_exit.is_set():
            await asyncio.sleep(1)
        self._consumer.stop()
        self.logger.info("consumer has terminated")

        self.ensure_exit()

    def on_run(self):
        consumer = asyncio.create_task(self.consumer())
        writer = asyncio.create_task(self.writer())
        return [writer, consumer]


def main():
    PgSink().run()


if __name__ == "__main__":
    main()
