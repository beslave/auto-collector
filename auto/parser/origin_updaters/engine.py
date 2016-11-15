from auto.models import OriginEngine
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEngineUpdater(OriginUpdater):
    table = OriginEngine.__table__
    comparable_fields = ['complectation_id']
