import asyncio
import logging

import settings

from auto.parser.ria import RiaNewParser, RiaUsedParser


logger = logging.getLogger('auto.parser')


def get_parsers(*args, **kwargs):
    return map(lambda Parser: Parser(*args, **kwargs), [
        RiaNewParser,
        RiaUsedParser,
    ])


def get_parser_task(parser):
    async def parser_task():
        while True:
            try:
                await parser.parse()
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(settings.SYNC_TIMEOUT)

    return parser_task


tasks = [
	get_parser_task(parser)
	for parser in get_parsers()
]
