from auto.models import OriginComplectation
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginComplectationUpdater(OriginUpdater):
    table = OriginComplectation.__table__
    comparable_fields = ['model_id', 'name']
    api_fields = {'name': 'complectation'}
    field_dependencies = {
        'model_id': 'model.id',
    }
