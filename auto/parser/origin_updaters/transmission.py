from auto.models import OriginTransmission
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginTransmissionUpdater(OriginUpdater):
    table = OriginTransmission.__table__
    comparable_fields = ['complectation_id']
