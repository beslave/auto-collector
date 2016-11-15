from auto.models import OriginEngineCylindersPosition
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEngineCylindersPositionUpdater(OriginUpdater):
    table = OriginEngineCylindersPosition.__table__
    comparable_fields = ['name']
    api_fields = {
        'name': 'cylinders_position',
    }
