module.exports = function ($resource) {
    return {
        BodyType: $resource('/api/body-types/:bodyTypeId/', {bodyTypeId: '@id'}),
        Brand: $resource('/api/brands/:brandId/', {brandId: '@id'}),
        EnergySource: $resource('/api/energy-sources/:energySourceId/', {energySourceId: '@id'}),
        Model: $resource('/api/models/:modelId/', {modelId: '@id'})
    };
};
