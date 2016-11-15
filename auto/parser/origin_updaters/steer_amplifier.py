from auto.models import OriginSteerAmplifier
from auto.parser.origin_updaters.base_origin_updater import OriginUpdater


class OriginSteerAmplifierUpdater(OriginUpdater):
    table = OriginSteerAmplifier.__table__
    comparable_fields = ['name']
    api_fields = {
        'name': 'steer_amplifier',
    }