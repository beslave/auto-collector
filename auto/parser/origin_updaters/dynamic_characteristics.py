from auto.models import OriginDynamicCharacteristics
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginDynamicCharacteristicsUpdater(OriginUpdater):
    table = OriginDynamicCharacteristics.__table__
    comparable_fields = ['complectation_id']