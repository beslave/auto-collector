from auto.models import OriginAdvertisement
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater
from auto.updaters import UpdateByCreatedAtMixin, UpdaterWithDatesMixin


class OriginAdvertisementUpdater(UpdateByCreatedAtMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginAdvertisement.__table__
    comparable_fields = ['name', 'model_id', 'complectation_id']
    api_fields = {
        'id': 'id',
        'name': 'name',
        'is_new': 'is_new',
        'year': 'year',
        'price': 'price',
        'preview': 'preview',
        'origin_url': 'url',
    }
    field_dependencies = {
        'model_id': 'model.id',
        'complectation_id': 'complectation.id',
        'state_id': 'state.id',
    }
