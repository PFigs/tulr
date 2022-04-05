import asyncio
import uvloop
import logging
import sys
import signal


class AioBase:
    def __init__(self, level="INFO", logger=None):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        self.logger = logger or logging.getLogger("turl")
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            level = "INFO"
        self.logger.setLevel(level=level)

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        asyncio.run(self._run())

    async def _run(self):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.notify_exit)
        loop.add_signal_handler(signal.SIGUSR1, self.notify_exit)
        tasks = self.on_run()
        await asyncio.gather(*tasks)
        self.on_exit()

    def on_run(self):
        raise NotImplementedError

    def on_exit(self):
        pass

    def ensure_exit(self):
        if not self.signal_exit.is_set():
            self.signal_exit.set()

    def notify_exit(self):
        self.signal_exit.set()
        self.logger.info("Exit signal has been set")
