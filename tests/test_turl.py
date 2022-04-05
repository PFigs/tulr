import pathlib
import threading
import time
import unittest

import yaml

from turl import Turl


class TestTurl(unittest.TestCase):
    def setUp(self) -> None:
        config_filepath = "./turl.yaml"
        with pathlib.Path(config_filepath) as filepath:
            self.config_file = yaml.load(filepath.read_text(), Loader=yaml.SafeLoader)
        self.turl_obj = Turl(config_filepath=config_filepath)

    def consume_queue(
        self, responses_queue, signal_exit, expect_results, max_timeout=10
    ):

        timeout = 0
        all_done = False

        hosts = set(expect_results.keys())
        observed_results = {k: 0 for k in hosts}

        while timeout < max_timeout:
            all_done = True
            msg = responses_queue.get()
            observed_host = msg.url
            self.assertTrue(observed_host in hosts)
            observed_results[observed_host] += 1
            print(observed_host, observed_results[observed_host])
            for host, observed_count in observed_results.items():
                print(
                    f"{observed_host} seen:{observed_results[observed_host]} expected: {expect_results[host]}"
                )
                if observed_count >= expect_results[host]:
                    all_done &= True
                else:
                    all_done &= False
            print(all_done)
            if all_done:
                break

            timeout += 1
            time.sleep(1)

        signal_exit.set()
        self.assertTrue(all_done)

    def test_setup_turl(self):

        expected_results = {
            host: 1 for host in self.config_file["turl"]["hosts"].keys()
        }

        max_timeout = 0
        for host, host_details in self.config_file["turl"]["hosts"].items():
            if "rate" in host_details:
                max_timeout = max(max_timeout, host_details["rate"] * 2)

        turl_thd = threading.Thread(
            target=self.consume_queue,
            kwargs=dict(
                responses_queue=self.turl_obj.responses_queue,
                signal_exit=self.turl_obj.signal_exit,
                expect_results=expected_results,
                max_timeout=max_timeout,
            ),
        )

        turl_thd.start()

        # assert message
        self.turl_obj.run()
        turl_thd.join()
