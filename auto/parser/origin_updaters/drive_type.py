from auto.models import OriginDriveType
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginDriveTypeUpdater(OriginUpdater):
    table = OriginDriveType.__table__
    comparable_fields = ['name']
