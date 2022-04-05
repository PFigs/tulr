import pathlib
import threading
import time
import unittest

import yaml

from turl import PgSink


class TestPgSink(unittest.TestCase):
    def setUp(self) -> None:
        config_filepath = "./turl.yaml"
        with pathlib.Path(config_filepath) as filepath:
            self.config_file = yaml.load(filepath.read_text(), Loader=yaml.SafeLoader)
        self.pg_sink = PgSink(config_filepath=config_filepath)

    def wait_for_connect(self, wait_for_writer, signal_exit, max_timeout=61):
        timeout = 0
        while timeout < max_timeout:
            if wait_for_writer.is_set():
                break
            time.sleep(1)
        signal_exit.set()
        self.assertTrue(wait_for_writer.is_set())

    def test_pg_sink_connection(self):

        pg_sink_thd = threading.Thread(
            target=self.wait_for_connect,
            kwargs=dict(
                wait_for_writer=self.pg_sink.wait_for_writer,
                signal_exit=self.pg_sink.signal_exit,
                max_timeout=10,
            ),
        )

        pg_sink_thd.start()

        # assert message
        self.pg_sink.run()
        pg_sink_thd.join()
