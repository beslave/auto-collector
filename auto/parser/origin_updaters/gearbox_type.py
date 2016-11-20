from auto.models import OriginGearboxType
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginGearboxTypeUpdater(OriginUpdater):
    table = OriginGearboxType.__table__
    comparable_fields = ['name']
    api_fields = {
        'name': 'gearbox_type',
    }
