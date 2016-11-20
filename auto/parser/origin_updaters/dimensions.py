from auto.models import OriginDimensions
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginDimensionsUpdater(OriginUpdater):
    table = OriginDimensions.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'length': 'length',
        'width': 'width',
        'height': 'height',
        'clearance': 'clearance',
        'curb_weight': 'curb_weight',
        'max_allowed_weight': 'max_allowed_weight',
        'trunk_volume': 'trunk_volume',
        'fuel_tank_volume': 'fuel_tank_volume',
        'wheel_base': 'wheel_base',
        'bearing_capacity': 'bearing_capacity',
    }
    field_dependencies = {
        'complectation_id': 'complectation.id',
    }
