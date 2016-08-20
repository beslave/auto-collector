__all__ = (
    'ConnectionManager',
)

import aiopg.sa.engine

from auto import settings


class ConnectionManager:
    async def __aenter__(self):
        if not hasattr(self.__class__, 'engine'):
            self.__class__.engine = await aiopg.sa.engine._create_engine(**settings.DATABASE)

        self.connection = await self.__class__.engine.acquire()
        return self.connection

    async def __aexit__(self, *args):
        try:
            await self.engine.release(self.connection)
        except AssertionError as e:
            pass
        self.connection = None
