from auto.models import OriginEngineFuelRate
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEngineFuelRateUpdater(OriginUpdater):
    table = OriginEngineFuelRate.__table__
