from auto.models import OriginBodyType
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginBodyTypeUpdater(OriginUpdater):
    table = OriginBodyType.__table__
    comparable_fields = ['name']
