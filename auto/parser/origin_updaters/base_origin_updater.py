import re

from auto.updaters import Updater


class OriginUpdater(Updater):
    origin_field = 'origin'
    origin = None
    api_fields = {}
    field_dependencies = {}

    def __init__(self, origin=None, *args, **kwargs):
        self.origin = origin or self.origin
        self.name = self.__class__.__name__.replace('Origin', '').replace('Updater', '')
        self.name = re.subn(r'(?!^)([A-Z])', r'_\1', self.name)[0].lower()
        super().__init__(*args, **kwargs)

    def complete_query(self, query):
        query = super().complete_query(query)
        query = query.where(self.table.c.origin == self.origin)
        return query

    def get_updater_name(self):
        return '{}: {}'.format(super().get_updater_name(), self.origin)

    async def preprocess_data(self, data):
        data = await super().preprocess_data(data)

        if data:
            data[self.origin_field] = self.origin

        return data