from auto.models import OriginEngineFuelRate
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEngineFuelRateUpdater(OriginUpdater):
    table = OriginEngineFuelRate.__table__
    api_fields = {
        'mixed': 'engine_fuel_rate_mixed',
        'urban': 'engine_fuel_rate_urban',
        'extra_urban': 'engine_fuel_rate_extra_urban',
    }
    field_dependencies = {
        'id': 'engine.id',
    }
    required_fields = ['mixed']
