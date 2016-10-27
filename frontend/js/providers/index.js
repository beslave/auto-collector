exports.autoData = function () {
    var data = {
        brands: [],
        brandsPrimaryIndex: {},
        models: [],
        modelsPrimaryIndex: {},
        filters: [],

        getBrand: function (brandId) {
            return this.brandsPrimaryIndex[brandId];
        },
        getModel: function (modelId) {
            return this.modelsPrimaryIndex[modelId];
        }
    };

    var syncPrimaryIndex = function (data, dataIndex, primaryKey) {
        data.forEach(function (item) {
            var pk = item[primaryKey];
            dataIndex[pk] = item;
        });
    };

    this.$get = function ($rootScope, $resource) {
        var Brand = $resource('/api/brands/:brandId', {brandId: '@id'});
        var Model = $resource('/api/models/:modelId', {modelId: '@id'});
        data.brands = Brand.query(function (results) {
            data.models = Model.query(function (results) {
                data.models.forEach(function (model) {
                    model.brand = data.getBrand(model.brand_id);
                });
                syncPrimaryIndex(data.models, data.modelsPrimaryIndex, 'id');
                $rootScope.$broadcast('autoDataChanged', data);
            });
            syncPrimaryIndex(data.brands, data.brandsPrimaryIndex, 'id');
        });
        return data;
    };
};