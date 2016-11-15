from auto.models import OriginEnginePower
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEnginePowerUpdater(OriginUpdater):
    table = OriginEnginePower.__table__
    api_fields = {
        'horses': 'engine_power_horses',
        'rotations_start': 'engine_power_rotations_start',
        'rotations_end': 'engine_power_rotations_end',
        'max_torque': 'engine_power_max_torque',
        'max_torque_rotations_start': 'engine_power_max_torque_rotations_start',
        'max_torque_rotations_end': 'engine_power_max_torque_rotations_end',
    }
    field_dependencies = {
        'id': 'engine.id',
    }
