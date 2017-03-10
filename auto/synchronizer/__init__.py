import asyncio
import logging
import psycopg2

import settings

from auto.connection import ConnectionManager
from auto.models import (
    Body, OriginBody,
    BodyType, OriginBodyType,
    Brand, OriginBrand,
    Model, OriginModel,
    Advertisement, OriginAdvertisement,
    Complectation, OriginComplectation,
    Dimensions, OriginDimensions,
    EnginePosition, OriginEnginePosition,
    EnergySource, OriginEnergySource,
    EngineCylindersPosition, OriginEngineCylindersPosition,
    Engine, OriginEngine,
    EnginePower, OriginEnginePower,
    EngineFuelRate, OriginEngineFuelRate,
    GearboxType, OriginGearboxType,
    DriveType, OriginDriveType,
    Transmission, OriginTransmission,
    State, OriginState,
    SteerAmplifier, OriginSteerAmplifier,
    Steering, OriginSteering,
    DynamicCharacteristics, OriginDynamicCharacteristics,
)
from auto.updaters import SynchronizerUpdater
from auto.utils import make_db_query


logger = logging.getLogger('auto.synchronizer')


class StateUpdater(SynchronizerUpdater):
    table = State.__table__
    origin_table = OriginState.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class BodyTypeUpdater(SynchronizerUpdater):
    table = BodyType.__table__
    origin_table = OriginBodyType.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class EnginePositionUpdater(SynchronizerUpdater):
    table = EnginePosition.__table__
    origin_table = OriginEnginePosition.__table__
    comparable_fields = ['name']


class EnergySourceUpdater(SynchronizerUpdater):
    table = EnergySource.__table__
    origin_table = OriginEnergySource.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class EngineCylindersPositionUpdater(SynchronizerUpdater):
    table = EngineCylindersPosition.__table__
    origin_table = OriginEngineCylindersPosition.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class GearboxTypeUpdater(SynchronizerUpdater):
    table = GearboxType.__table__
    origin_table = OriginGearboxType.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class DriveTypeUpdater(SynchronizerUpdater):
    table = DriveType.__table__
    origin_table = OriginDriveType.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class SteerAmplifierUpdater(SynchronizerUpdater):
    table = SteerAmplifier.__table__
    origin_table = OriginSteerAmplifier.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class BrandUpdater(SynchronizerUpdater):
    table = Brand.__table__
    origin_table = OriginBrand.__table__
    sync_fields = ['name']
    comparable_fields = ['name']


class ModelUpdater(SynchronizerUpdater):
    table = Model.__table__
    origin_table = OriginModel.__table__
    comparable_fields = ['name', 'brand_id']
    sync_fields = ['name', 'brand_id']
    comparable_fields = ['name']

    async def preprocess_data(self, data):
        if data:
            data['brand_id'] = await self.get_real_instance(OriginBrand, data['origin'], data['brand_id'])

            if not data['brand_id']:
                data = None

        return await super().preprocess_data(data)


class ComplectationUpdater(SynchronizerUpdater):
    table = Complectation.__table__
    origin_table = OriginComplectation.__table__
    sync_fields = [
        'name',
        'model_id',
    ]
    comparable_fields = ['name', 'model_id']

    async def preprocess_data(self, data):
        if data:
            data['model_id'] = await self.get_real_instance(OriginModel, data['origin'], data['model_id'])

            if not data['model_id']:
                data = None

        return await super().preprocess_data(data)


class BodyUpdater(SynchronizerUpdater):
    table = Body.__table__
    origin_table = OriginBody.__table__
    sync_fields = [
        'complectation_id',
        'body_type_id',
        'doors',
        'seats',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])
            data['body_type_id'] = await self.get_real_instance(OriginBodyType, data['origin'], data['body_type_id'])

            if not (data['complectation_id'] and data['body_type_id']):
                data = None

        return await super().preprocess_data(data)


class DimensionsUpdater(SynchronizerUpdater):
    table = Dimensions.__table__
    origin_table = OriginDimensions.__table__
    sync_fields = [
        'complectation_id',
        'length',
        'width',
        'height',
        'clearance',
        'curb_weight',
        'max_allowed_weight',
        'trunk_volume',
        'fuel_tank_volume',
        'wheel_base',
        'bearing_capacity',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])

            if not data['complectation_id']:
                data = None

        return await super().preprocess_data(data)


class EngineUpdater(SynchronizerUpdater):
    table = Engine.__table__
    origin_table = OriginEngine.__table__
    sync_fields = [
        'complectation_id',
        'position_id',
        'energy_source_id',
        'volume',
        'cylinders',
        'cylinders_position_id',
        'valves_count',
        'co2_emission',
        'euro_toxicity_norms',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])
            data['position_id'] = await self.get_real_instance(OriginEnginePosition, data['origin'], data['position_id'])
            data['energy_source_id'] = await self.get_real_instance(OriginEnergySource, data['origin'], data['energy_source_id'])

            if not (data['complectation_id'] and data['position_id'] and data['energy_source_id']):
                data = None

        return await super().preprocess_data(data)


class EnginePowerUpdater(SynchronizerUpdater):
    table = EnginePower.__table__
    origin_table = OriginEnginePower.__table__
    real_instance_table = OriginEngine.__table__
    sync_fields = [
        'horses',
        'rotations_start',
        'rotations_end',
        'max_torque',
        'max_torque_rotations_start',
        'max_torque_rotations_end',
    ]
    comparable_fields = []


class EngineFuelRateUpdater(SynchronizerUpdater):
    table = EngineFuelRate.__table__
    origin_table = OriginEngineFuelRate.__table__
    real_instance_table = OriginEngine.__table__
    sync_fields = [
        'mixed',
        'urban',
        'extra_urban',
    ]
    comparable_fields = []


class TransmissionUpdater(SynchronizerUpdater):
    table = Transmission.__table__
    origin_table = OriginTransmission.__table__
    sync_fields = [
        'complectation_id',
        'gearbox_type_id',
        'gears_count',
        'drive_type_id',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])
            data['gearbox_type_id'] = await self.get_real_instance(OriginGearboxType, data['origin'], data['gearbox_type_id'])
            data['drive_type_id'] = await self.get_real_instance(OriginDriveType, data['origin'], data['drive_type_id'])

            if not (data['complectation_id'] and data['gearbox_type_id'] and data['drive_type_id']):
                data = None

        return await super().preprocess_data(data)


class SteeringUpdater(SynchronizerUpdater):
    table = Steering.__table__
    origin_table = OriginSteering.__table__
    sync_fields = [
        'complectation_id',
        'amplifier_id',
        'spread_diameter',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])

            if not data['complectation_id']:
                data = None

        return await super().preprocess_data(data)


class DynamicCharacteristicsUpdater(SynchronizerUpdater):
    table = DynamicCharacteristics.__table__
    origin_table = OriginDynamicCharacteristics.__table__
    sync_fields = [
        'complectation_id',
        'max_velocity',
        'acceleration_time_to_100',
    ]
    comparable_fields = ['complectation_id']

    async def preprocess_data(self, data):
        if data:
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])

            if not data['complectation_id']:
                data = None

        return await super().preprocess_data(data)


class AdvertisementUpdater(SynchronizerUpdater):
    table = Advertisement.__table__
    origin_table = OriginAdvertisement.__table__
    sync_fields = [
        'name',
        'model_id',
        'complectation_id',
        'state_id',
        'is_new',
        'year',
        'price',
        'origin_url',
        'preview',
    ]
    shorten_url_fields = ['origin_url', 'preview']
    comparable_fields = []

    async def preprocess_data(self, data):
        if data:
            data['model_id'] = await self.get_real_instance(OriginModel, data['origin'], data['model_id'])
            data['complectation_id'] = await self.get_real_instance(OriginComplectation, data['origin'], data['complectation_id'])

            if not (data['model_id'] and data['complectation_id']):
                data = None

        return await super().preprocess_data(data)


class Synchronizer:
    updaters_list = [
        StateUpdater,
        BodyTypeUpdater,
        EnginePositionUpdater,
        EnergySourceUpdater,
        EngineCylindersPositionUpdater,
        GearboxTypeUpdater,
        DriveTypeUpdater,
        SteerAmplifierUpdater,
        BrandUpdater,
        ModelUpdater,
        ComplectationUpdater,
        BodyUpdater,
        DimensionsUpdater,
        EngineUpdater,
        EnginePowerUpdater,
        EngineFuelRateUpdater,
        SteeringUpdater,
        DynamicCharacteristicsUpdater,
        AdvertisementUpdater,
    ]

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__instance__', None):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)

        return cls.__instance__

    async def init_updaters(self):
        if getattr(self, 'is_updaters_initialized', False):
            return

        self.updaters = []
        for updater_class in self.updaters_list:
            updater = await updater_class.new()
            self.updaters.append(updater)

        self.is_updaters_initialized = True


    async def run(self):
        while True:
            try:
                await self.teak()
            except Exception as e:
                logger.exception(e)

            await asyncio.sleep(settings.SYNC_TIMEOUT)

    async def teak(self):
        await self.init_updaters()

        for updater in self.updaters:
            await updater.sync()


synchronizer = Synchronizer()
tasks = [synchronizer.run]
