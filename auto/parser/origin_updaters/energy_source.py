from auto.models import OriginEnergySource
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEnergySourceUpdater(OriginUpdater):
    table = OriginEnergySource.__table__
    comparable_fields = ['name']
    api_fields = {
        'name': 'energy_source',
    }
