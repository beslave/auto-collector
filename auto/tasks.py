import asyncio
import json
import logging

from functools import wraps
from psycopg2 import IntegrityError

from auto import settings
from auto.parsers import get_parsers


logger = logging.getLogger('auto.tasks')


async def sync_data():
    for parser in get_parsers():
        await parser.parse()


async def sync_data_task():
    while True:
        logger.debug('{:=^40}'.format(' SYNC DATA '))
        try:
            await sync_data()
        except Exception as e:
            logger.exception(e)

        await asyncio.sleep(settings.SYNC_TIMEOUT)


tasks = [
    sync_data_task,
]
