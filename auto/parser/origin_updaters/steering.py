from auto.models import OriginSteering
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginSteeringUpdater(OriginUpdater):
    table = OriginSteering.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'spread_diameter': 'spread_diameter',
    }
    field_dependencies = {
        'complectation_id': 'complectation.id',
        'amplifier_id': 'steer_amplifier.id',
    }
