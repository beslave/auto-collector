import asyncio


class Parser(object):
    def __init__(self):
        self.number = 0
        self.adv_iterator = self.iter_advertisements()

    def iter_pages(self):
        yield None

    def iter_advertisements(self):
        for page in self.iter_pages():
            for x in range(5):
                yield None

    async def parse_advertisement(self, adv):
        self.number += 1
        return self.number

    async def __aiter__(self):
        return self

    async def __anext__(self):
        for adv_data in self.adv_iterator:
            return await self.parse_advertisement(adv_data)
        raise StopAsyncIteration
