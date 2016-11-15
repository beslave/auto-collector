from auto.models import OriginEngine
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginEngineUpdater(OriginUpdater):
    table = OriginEngine.__table__
    comparable_fields = ['complectation_id']
    api_fields = {
        'volume': 'engine_volume',
        'cylinders': 'engine_cylinders',
        'valves_count': 'engine_valves_count',
        'co2_emission': 'engine_co2_emission',
        'euro_toxicity_norms': 'engine_euro_toxicity_norms',
    }
    field_dependencies = {
        'complectation_id': 'complectation.id',
        'position_id': 'engine_position.id',
        'energy_source_id': 'energy_source.id',
        'cylinders_position_id': 'engine_cylinders_position.id',
    }