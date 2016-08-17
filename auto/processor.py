import asyncio
import functools

from concurrent.futures import ProcessPoolExecutor


class BaseProcessor:
    def __init__(self, max_workers=None):
        self.executor = ProcessPoolExecutor(max_workers)

    def do(self, *args, **kwargs):
        pass

    async def process(self, *args, **kwargs):
        do = functools.partial(self.do, *args, **kwargs)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, do)
