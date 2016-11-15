from auto.models import OriginSteering
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginSteeringUpdater(OriginUpdater):
    table = OriginSteering.__table__
    comparable_fields = ['complectation_id']
