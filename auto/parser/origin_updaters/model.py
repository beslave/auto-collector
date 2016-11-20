from auto.models import OriginModel
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater
from auto.updaters import UpdateNotSimilarMixin, UpdaterWithDatesMixin


class OriginModelUpdater(UpdateNotSimilarMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginModel.__table__
    comparable_fields = ['name', 'brand_id']
    api_fields = {'name': 'model'}
    field_dependencies = {
        'brand_id': 'brand.id',
    }
