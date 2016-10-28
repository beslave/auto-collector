module.exports = function ($resource) {
    return {
        Brand: $resource('/api/brands/:brandId/', {brandId: '@id'}),
        Model: $resource('/api/models/:modelId/', {modelId: '@id'})
    };
};
