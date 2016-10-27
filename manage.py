#! /usr/bin/python

import argparse
import asyncio
import logging.config

from app import app_handler
from auto import settings
from auto.tasks import tasks as parse_tasks


logging.config.dictConfig(settings.LOGGING)
loop = asyncio.get_event_loop()

serve_task = loop.create_server(app_handler, settings.SITE_ADDR, settings.SITE_PORT)
commands = {
    'parse': [asyncio.ensure_future(task()) for task in parse_tasks],
    'serve': serve_task,
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


def prepare_tasks_list(tasks):
    if not isinstance(tasks, list):
        tasks = [tasks]
    return tasks


if args.command == 'all':
    tasks = []
    for command_tasks in commands.values():
        tasks.extend(prepare_tasks_list(command_tasks))
else:
    command_tasks = commands[args.command]
    tasks = prepare_tasks_list(command_tasks)

loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()
loop.close()
