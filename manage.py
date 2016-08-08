import asyncio

from app import app_handler
from auto import settings
from auto.tasks import tasks as auto_tasks


loop = asyncio.get_event_loop()

tasks = [asyncio.ensure_future(task()) for task in auto_tasks] + [
    loop.create_server(app_handler, settings.SITE_ADDR, settings.SITE_PORT),
]
loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()
loop.close()