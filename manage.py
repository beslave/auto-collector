#! /usr/bin/python

import argparse
import asyncio
import logging.config

from auto import settings
from auto.parser import tasks as parse_tasks
from auto.server import tasks as serve_tasks
from auto.synchronizer import tasks as synchorize_tasks


logging.config.dictConfig(settings.LOGGING)
loop = asyncio.get_event_loop()


commands = {
    'parse': parse_tasks,
    'synchronize': synchorize_tasks,
    'serve': serve_tasks,
}

parser = argparse.ArgumentParser()
parser.add_argument(
    'command',
    nargs='?',
    choices=['all'] + list(commands.keys()),
    default='all',
    help='command name'
)
args = parser.parse_args()


if args.command == 'all':
    tasks = []
    for command_tasks in commands.values():
        tasks.extend(command_tasks)
else:
    command_tasks = commands[args.command]
    tasks = command_tasks


tasks_coroutine = [task() for task in tasks]

loop.run_until_complete(asyncio.gather(*tasks_coroutine))
loop.run_forever()
loop.close()
