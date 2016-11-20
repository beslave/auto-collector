__all__ = (
    'ConnectionManager',
)

import aiopg.sa.engine
import logging
import psycopg2

import settings


logger = logging.getLogger('auto.connection')


class ConnectionManager:
    async def __aenter__(self):
        while True:
            try:
                if not hasattr(self.__class__, 'engine'):
                    self.__class__.engine = await aiopg.sa.engine._create_engine(
                        **settings.DATABASE
                    )
                self.connection = await self.__class__.engine.acquire()
                return self.connection
            except psycopg2.OperationalError as e:
                logger.exception(e)


    async def __aexit__(self, *args):
        try:
            await self.engine.release(self.connection)
        except AssertionError as e:
            pass

        self.connection = None
