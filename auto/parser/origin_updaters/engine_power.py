from auto.models import OriginEnginePower
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEnginePowerUpdater(OriginUpdater):
    table = OriginEnginePower.__table__
