import asyncio
import json
import logging

from functools import wraps
from psycopg2 import IntegrityError

from auto import settings
from auto.parsers import get_parsers
from auto.synchronizer import Synchronizer


logger = logging.getLogger('auto.tasks')


def get_parser_task(parser):
    async def parser_task():
        while True:
            try:
                await parser.parse()
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(settings.SYNC_TIMEOUT)

    return parser_task


synchronizer = Synchronizer()

tasks = []
tasks += [get_parser_task(parser) for parser in get_parsers()]
tasks += [synchronizer.run]
