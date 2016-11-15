from auto.models import OriginEnginePosition
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEnginePositionUpdater(OriginUpdater):
    table = OriginEnginePosition.__table__
    comparable_fields = ['name']
