from auto.models import OriginState
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginStateUpdater(OriginUpdater):
    table = OriginState.__table__
    comparable_fields = ['name']
    api_fields = {'name': 'state'}
