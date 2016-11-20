from auto.models import OriginBody
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginBodyUpdater(OriginUpdater):
    table = OriginBody.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'doors': 'doors',
        'seats': 'seats',
    }
    field_dependencies = {
        'body_type_id': 'body_type.id',
        'complectation_id': 'complectation.id',
    }
