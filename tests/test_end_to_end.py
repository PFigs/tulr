import unittest


class TestEndToEnd(unittest.TestCase):
    def monitor(self):
        # Monitor messages in topic and exists when consumption has happened
        pass

    def test_end_to_end(self):
        # starts monitor on kafka topic
        # run tulr - exit signaled from monitor on N messages
        # run pg_sink - exit signaled from monitor after seeing N messages on topic + some delay (ideally it could track sink metrics)
        # assert N messages were written in postgres
        pass
