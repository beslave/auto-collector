import aiohttp
import asyncio
import logging

from auto.models import (
    OriginAdvertisement,
    OriginBrand,
    OriginModel,

    OriginComplectation,
    OriginBody,
    OriginBodyType,
    OriginDimensions,
    OriginEngine,
    OriginEnginePosition,
    OriginEnergySource,
    OriginEngineCylindersPosition,
    OriginEnginePower,
    OriginEngineFuelRate,
    OriginTransmission,
    OriginGearboxType,
    OriginDriveType,
    OriginSteering,
    OriginSteerAmplifier,
    OriginDynamicCharacteristics,
)
from auto.updaters import (
    OriginUpdater,
    UpdateByCreatedAtMixin,
    UpdateNotSimilarMixin,
    UpdaterWithDatesMixin,
)


class OriginBrandUpdater(UpdateNotSimilarMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginBrand.__table__
    condition_fields = ['name']


class OriginModelUpdater(UpdateNotSimilarMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginModel.__table__
    condition_fields = ['name']


class OriginAdvertisementUpdater(UpdateByCreatedAtMixin, UpdaterWithDatesMixin, OriginUpdater):
    table = OriginAdvertisement.__table__


class OriginComplectationUpdater(OriginUpdater):
    table = OriginComplectation.__table__
    comparable_fields = ['model_id', 'name']


class OriginBodyUpdater(OriginUpdater):
    table = OriginBody.__table__
    comparable_fields = ['complectation_id']


class OriginBodyTypeUpdater(OriginUpdater):
    table = OriginBodyType.__table__
    comparable_fields = ['name']


class OriginDimensionsUpdater(OriginUpdater):
    table = OriginDimensions.__table__
    comparable_fields = ['complectation_id']


class OriginEngineUpdater(OriginUpdater):
    table = OriginEngine.__table__
    comparable_fields = ['complectation_id']


class OriginEnginePositionUpdater(OriginUpdater):
    table = OriginEnginePosition.__table__
    comparable_fields = ['name']


class OriginEnergySourceUpdater(OriginUpdater):
    table = OriginEnergySource.__table__
    comparable_fields = ['name']


class OriginEngineCylindersPositionUpdater(OriginUpdater):
    table = OriginEngineCylindersPosition.__table__
    comparable_fields = ['name']


class OriginEnginePowerUpdater(OriginUpdater):
    table = OriginEnginePower.__table__


class OriginEngineFuelRateUpdater(OriginUpdater):
    table = OriginEngineFuelRate.__table__


class OriginTransmissionUpdater(OriginUpdater):
    table = OriginTransmission.__table__
    comparable_fields = ['complectation_id']


class OriginGearboxTypeUpdater(OriginUpdater):
    table = OriginGearboxType.__table__
    comparable_fields = ['name']


class OriginDriveTypeUpdater(OriginUpdater):
    table = OriginDriveType.__table__
    comparable_fields = ['name']


class OriginSteeringUpdater(OriginUpdater):
    table = OriginSteering.__table__
    comparable_fields = ['complectation_id']


class OriginSteerAmplifierUpdater(OriginUpdater):
    table = OriginSteerAmplifier.__table__
    comparable_fields = ['name']


class OriginDynamicCharacteristicsUpdater(OriginUpdater):
    table = OriginDynamicCharacteristics.__table__
    comparable_fields = ['complectation_id']


class BaseParser(object):
    ORIGIN = None
    MAX_GET_ATTEMPTS = 5

    brand_table = OriginBrand.__table__
    model_table = OriginModel.__table__
    advertisement_table = OriginAdvertisement.__table__

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = super().__new__(cls, *args, **kwargs)
        return cls.__instance__

    async def get_attempts(self, url, getter='json'):
        retries = 1
        while True:
            try:
                async with self.client.get(url) as response:
                    assert response.status < 400
                    return await getattr(response, getter)()

            except Exception as e:
                if retries > self.MAX_GET_ATTEMPTS:
                    raise

                await asyncio.sleep(1)
                retries += 1

    async def init_updaters(self):
        if getattr(self, 'is_initialized', False):
            return

        self.brand_updater = await OriginBrandUpdater.new(self.ORIGIN)
        self.model_updater = await OriginModelUpdater.new(self.ORIGIN)
        self.adv_updater = await OriginAdvertisementUpdater.new(self.ORIGIN)

        self.complectation_updater = await OriginComplectationUpdater.new(self.ORIGIN)
        self.body_updater = await OriginBodyUpdater.new(self.ORIGIN)
        self.body_type_updater = await OriginBodyTypeUpdater.new(self.ORIGIN)
        self.dimensions_updater = await OriginDimensionsUpdater.new(self.ORIGIN)
        self.engine_updater = await OriginEngineUpdater.new(self.ORIGIN)
        self.engine_position_updater = await OriginEnginePositionUpdater.new(self.ORIGIN)
        self.energy_source_updater = await OriginEnergySourceUpdater.new(self.ORIGIN)
        self.engine_cylinders_position_updater = await OriginEngineCylindersPositionUpdater.new(self.ORIGIN)
        self.engine_power_updater = await OriginEnginePowerUpdater.new(self.ORIGIN)
        self.engine_fuel_rate_updater = await OriginEngineFuelRateUpdater.new(self.ORIGIN)
        self.transmission_updater = await OriginTransmissionUpdater.new(self.ORIGIN)
        self.gearbox_type_updater = await OriginGearboxTypeUpdater.new(self.ORIGIN)
        self.drive_type_updater = await OriginDriveTypeUpdater.new(self.ORIGIN)
        self.steering_updater = await OriginSteeringUpdater.new(self.ORIGIN)
        self.steer_amplifier_updater = await OriginSteerAmplifierUpdater.new(self.ORIGIN)
        self.dynamic_characteristics_updater = await OriginDynamicCharacteristicsUpdater.new(self.ORIGIN)

        self.is_initialized = True

    async def parse(self):
        await self.init_updaters()

        with aiohttp.ClientSession() as client:
            self.client = client
            await self.parse_brands()
            await self.parse_models()
            await self.parse_advertisements()

    async def parse_brands(self):
        raise NotImplemented

    async def parse_models(self):
        raise NotImplemented

    async def parse_advertisements(self):
        pass
