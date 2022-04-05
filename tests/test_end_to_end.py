import pathlib
import unittest

import yaml

from turl import Turl, PgSink


class TestEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        config_filepath = "./turl.yaml"
        with pathlib.Path(config_filepath) as filepath:
            self.config_file = yaml.load(filepath.read_text(), Loader=yaml.SafeLoader)

        self.turl_obj = Turl(config_filepath=config_filepath)
        self.pg_sink = PgSink(config_filepath=config_filepath)

    def monitor(self):
        # Monitor messages in topic and exists when consumption has happened
        pass

    def test_end_to_end(self):
        # starts monitor on kafka topic
        # run tulr - exit signaled from monitor on N messages
        # run pg_sink - exit signaled from monitor after seeing N messages on topic + some delay (ideally it could track sink metrics)
        # assert N messages were written in postgres
        pass
