from auto.models import OriginDynamicCharacteristics
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginDynamicCharacteristicsUpdater(OriginUpdater):
    table = OriginDynamicCharacteristics.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'max_velocity': 'max_velocity',
        'acceleration_time_to_100': 'acceleration_time_to_100',
    }
    field_dependencies = {
        'complectation_id': 'complectation.id',
    }