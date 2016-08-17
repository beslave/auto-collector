import logging

from datetime import datetime
from psycopg2 import IntegrityError
from random import random
from sqlalchemy.sql import select

from auto import settings
from auto.utils import make_db_query, shorten_url


logger = logging.getLogger('auto.updater')


class Updater:
    pk_field = 'id'
    condition_fields = []
    shorten_url_fields = []
    table = None

    @classmethod
    async def new(cls, *args, **kwargs):
        self = cls(*args, **kwargs)

        async def get_condition_cache(rows):
            cache = {}
            async for row in rows:
                cache[getattr(row, self.pk_field)] = [
                    getattr(row, field) for field in self.condition_fields
                ]
            return cache

        fields = list(set([self.pk_field] + self.condition_fields))
        query = select(getattr(self.table.c, field) for field in fields)
        self.cache = await make_db_query(self.complete_query(query), get_condition_cache)
        self.not_updated = set(self.cache.keys())
        return self

    def __init__(self, table=None, shorten_url_fields=None):
        if table is not None:
            self.table = table

        if shorten_url_fields is not None:
            self.shorten_url_fields = shorten_url_fields

    def __iter__(self):
        for pk in self.cache:
            yield pk

    def complete_query(self, query):
        return query

    def get_update_probability(self, data, **kwargs):
        return 0

    def get_condition_data(self, pk):
        return dict(zip(self.condition_fields, self.cache[pk]))

    async def preprocess_data(self, data):
        processed = {}
        for field, value in data.items():
            if field in self.shorten_url_fields:
                value = await shorten_url(value)

            processed[field] = value

        return processed

    def get_updater_name(self):
        return self.__class__.__name__

    def get_log_message(self, msg, *args, **kwargs):
        msg = msg.format(*args, **kwargs)
        return '({}) {}'.format(self.get_updater_name(), msg)

    async def update(self, data):
        data = await self.preprocess_data(data)

        pk = data.get(self.pk_field)
        self.not_updated.discard(pk)

        if pk not in self.cache:
            return await self.create(data)

        conditions = self.get_condition_data(pk)
        update_probability = self.get_update_probability(data, **conditions)

        if update_probability >= random():
            query = self.table.update().values(**data).where(self.table.c.id == pk)
            try:
                await make_db_query(self.complete_query(query))
                logger.debug(self.get_log_message('{}: Update #{}', self.table.name, pk))
            except IntegrityError as e:
                logger.warning(self.get_log_message(e))

        return pk

    async def create(self, data):
        pk = data[self.pk_field]

        if not pk:
            del data[self.pk_field]

        query = self.table.insert().values(**data)

        async def get_insert_id(rows):
            async for row in rows:
                return getattr(row, self.pk_field)

        try:
            if not pk:
                pk = await make_db_query(query, processor=get_insert_id)
            else:
                await make_db_query(query)

            data[self.pk_field] = pk
            self.cache[pk] = [data.get(x) for x in self.condition_fields]
            logger.debug(self.get_log_message('{}: Create #{}', self.table.name, pk))
            return pk
        except IntegrityError as e:
            logger.warning(e)

    async def delete_not_updated(self):
        if self.not_updated:
            pk_field = getattr(self.table.c, self.pk_field)
            query = self.table.delete().where(pk_field.in_(self.not_updated))
            result = await make_db_query(self.complete(query))

            for pk in self.not_updated:
                self.cache.pop(pk, None)

            msg = self.get_log_message('{}: {} objects were removed!', self.table.name, len(self.not_updated))
            logger.debug(msg)

        self.not_updated = set(self.cache.keys())


class UpdaterWithDates(Updater):
    created_at_field = 'created_at'
    updated_at_field = 'updated_at'

    async def create(self, data):
        data[self.created_at_field] = datetime.now()
        return await super().create(data)

    async def preprocess_data(self, data):
        data = await super().preprocess_data(data)
        data[self.updated_at_field] = datetime.now()
        return data


class OriginUpdater(UpdaterWithDates):
    origin_field = 'origin'
    origin = None

    def __init__(self, origin=None, *args, **kwargs):
        self.origin = origin or self.origin
        super().__init__(*args, **kwargs)

    def complete_query(self, query):
        query = super().complete_query(query)
        query = query.where(self.table.c.origin == self.origin)
        return query

    def get_updater_name(self):
        return '{}: {}'.format(super().get_updater_name(), self.origin)

    async def preprocess_data(self, data):
        data = await super().preprocess_data(data)
        data[self.origin_field] = self.origin
        return data


class SynchronizerUpdater(UpdaterWithDates):
    condition_fields = ['name', 'created_at', 'updated_at']
    comparable_fields = ['name',]
    sync_fields = []

    def get_update_probability(self, data, **kwargs):
        return 0

    def get_pk_for_data(self, data):
        for pk in self.cache:
            condition_data = self.get_condition_data(pk)
            if all(condition_data[field] == data[field] for field in self.comparable_fields):
                return pk

    async def preprocess_data(self, data):
        pk = data.get(self.pk_field) or self.get_pk_for_data(data)
        data = {
            field: data.get(field)
            for field in self.sync_fields
        }
        data[self.pk_field] = pk
        return await super().preprocess_data(data)


class UpdateNotSimilarMixin:
    def get_update_probability(self, data, **conditions):
        for condition, value in conditions.items():
            if data[condition] != value:
                return 1

        return 0


class UpdateByCreatedAtMixin:
    threshold = 60 * 60 * 24

    def __init__(self, *args, **kwargs):
        if self.created_at_field not in self.condition_fields:
            self.condition_fields.append(self.created_at_field)

        return super().__init__(*args, **kwargs)

    def get_update_probability(self, data, created_at=None, **kwargs):
        if not created_at:
            return 1.0

        delta_seconds = (datetime.now() - created_at).total_seconds()

        if delta_seconds < self.threshold:
            return delta_seconds / self.threshold
        else:
            return self.threshold / delta_seconds
