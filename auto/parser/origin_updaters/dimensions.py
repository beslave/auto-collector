from auto.models import OriginDimensions
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginDimensionsUpdater(OriginUpdater):
    table = OriginDimensions.__table__
    comparable_fields = ['complectation_id']
