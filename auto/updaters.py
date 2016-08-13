from aiopg.sa import create_engine
from datetime import datetime
from psycopg2 import IntegrityError
from random import random
from sqlalchemy.sql import select

from auto import settings
from auto.utils import log


async def make_db_query(query, processor=None):
    async with create_engine(**settings.DATABASE) as engine:
        async with engine.acquire() as connection:
            results = await connection.execute(query)
            
            if processor:
                return processor(results)

            return results


class Updater:
    table = None
    pk_field = 'id'
    condition_fields = []

    @classmethod
    async def new(cls, *args, **kwargs):
        self = cls(*args, **kwargs)
        fields = [self.pk_field] + self.condition_fields
        query = select([getattr(self.table.c, field) for field in fields])
        self.cache = await make_db_query(query, lambda rows: {
            getattr(row, self.pk_field): [
                getattr(row, field)
                for field in self.condition_fields
            ]
            for row in rows
        })
        self.not_updated = set(self.cache.keys())
        return self

    def get_update_probability(self, **kwargs):
        return 0

    def get_condition_data(self, pk):
        return dict(zip(self.condition_fields, self.cache[pk]))

    async def update(self, data):
        pk = data.get(self.pk_field)
        self.not_updated.discard(pk)
        if pk not in self.cache:
            return await self.create(data)

        conditions = self.get_condition_data(pk)
        update_probability = self.get_update_probability(**conditions)

        if update_probability >= random():
            query = self.table.update().values(**data).where(self.table.c.id == pk)
            try:
                return await make_db_query(query)
            except IntegrityError as e:
                log(e)

    async def create(self, data):
        pk = data.get(self.pk_field)
        if pk in self.cache:
            return await update(self, data)

        self.cache[pk] = [data.get(x) for x in self.condition_fields]
        query = self.table.insert().values(**data)

        try:
            return await make_db_query(query)
        except IntegrityError as e:
            log(e)

    async def delete_not_updated(self):
        if self.not_updated:
            pk_field = getattr(self.table.c, self.pk_field)
            query = self.table.delete().where(pk_field.in_(self.not_updated))
            result = await make_db_query(query)
            log('{}: {} objects were removed!', self.table.name, len(self.not_updated))

        self.not_updated = set(self.cache.keys())


class UpdaterByCreatedAt(Updater):
    threshold = 60 * 60 * 24
    created_at_field = 'created_at'

    def __init__(self, *args, **kwargs):
        if self.created_at_field not in self.condition_fields:
            self.condition_fields.append(self.created_at_field)

        return super().__init__(*args, **kwargs)

    def get_update_probability(self, created_at=None, **kwargs):
        if not created_at:
            return 1.0

        delta_seconds = (datetime.now() - created_at).total_seconds()

        if delta_seconds < self.threshold:
            return delta_seconds / self.threshold
        else:
            return self.threshold / delta_seconds

    async def create(self, data):
        data[self.created_at_field] = datetime.now()
        return await super().create(data)