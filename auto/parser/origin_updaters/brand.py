from auto.models import OriginBrand
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater
from auto.updaters import UpdateNotSimilarMixin, UpdaterWithDatesMixin


class OriginBrandUpdater(UpdateNotSimilarMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginBrand.__table__
    comparable_fields = ['name']
    api_fields = {'name': 'brand'}
