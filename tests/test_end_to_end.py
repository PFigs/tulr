import asyncio
import pathlib
import threading
import time
import unittest
import aiopg

import yaml

from turl import PgSink
from turl import Turl


class TestEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        config_filepath = "./turl.yaml"
        with pathlib.Path(config_filepath) as filepath:
            self.config_file = yaml.load(filepath.read_text(), Loader=yaml.SafeLoader)
        self.pg_sink = PgSink(config_filepath=config_filepath)
        self.turl_obj = Turl(config_filepath=config_filepath)

    def wait_for_turl(self, wait_for, signal_exit):
        # Monitor messages in topic and exists when consumption has happened
        time.sleep(wait_for)
        signal_exit.set()

    def wait_for_sink(self, wait_for_writer, signal_exit, sleep_for, max_timeout=60):
        # this thread should actually consume from kafka and then check in the db that the record was written
        timeout = 0
        while timeout < max_timeout:
            if wait_for_writer.is_set():
                break
            time.sleep(1)

        if not wait_for_writer.is_set():
            self.assertTrue(False)

        time.sleep(sleep_for)

        signal_exit.set()

    async def check_results(self):
        # assert there is data in pg
        dsn = " ".join([f"{k}={v}" for k, v in self.config_file["pg"].items()])
        async with aiopg.create_pool(dsn) as pool:
            async with pool.acquire() as pg_connection:
                async with pg_connection.cursor() as pg_cursor:
                    await pg_cursor.execute("SELECT * FROM RECORDS;")
                    results = []
                    async for row in pg_cursor:
                        results.append(row)
        return results

    def test_end_to_end(self):
        # wait for kafka to settle + at least a publish event to happen
        wait_for = 0
        for host, host_details in self.config_file["turl"]["hosts"].items():
            if "rate" in host_details:
                wait_for = max(wait_for, host_details["rate"] * 2)

        turl_thd = threading.Thread(
            target=self.wait_for_turl,
            kwargs=dict(
                wait_for=wait_for,
                signal_exit=self.turl_obj.signal_exit,
            ),
        )

        turl_thd.start()
        # assert message
        self.turl_obj.run()
        turl_thd.join()

        # waits for sink
        pg_sink_thd = threading.Thread(
            target=self.wait_for_sink,
            kwargs=dict(
                wait_for_writer=self.pg_sink.wait_for_writer,
                signal_exit=self.pg_sink.signal_exit,
                sleep_for=10,
            ),
        )

        pg_sink_thd.start()

        # assert message
        self.pg_sink.run()
        pg_sink_thd.join()

        results = asyncio.run(self.check_results())
        if not results:
            self.assertTrue(False)
