from auto.models import OriginTransmission
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginTransmissionUpdater(OriginUpdater):
    table = OriginTransmission.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'gears_count': 'gears_count',
    }
    field_dependencies = {
        'complectation_id': 'complectation.id',
        'gearbox_type_id': 'gearbox_type.id',
        'drive_type_id': 'drive_type.id',
    }
