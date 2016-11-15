from auto.models import OriginBody
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginBodyUpdater(OriginUpdater):
    table = OriginBody.__table__
    comparable_fields = ['complectation_id']
