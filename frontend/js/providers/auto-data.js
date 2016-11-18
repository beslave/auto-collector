module.exports = function () {
    var data = {
        bodyTypes: [],
        bodyTypesPrimaryIndex: {},
        brands: [],
        brandsPrimaryIndex: {},
        models: [],
        modelsPrimaryIndex: {},
        filters: [],

        getBodyType: function (bodyTypeId) {
            return this.bodyTypesPrimaryIndex[brandId];
        },
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

    this.$get = function ($rootScope, $resource, resourceModels) {
        data.bodyTypes = resourceModels.BodyType.query(function (results) {
            syncPrimaryIndex(data.bodyTypes, data.bodyTypesPrimaryIndex, 'id');
            $rootScope.$broadcast('autoDataChanged', data);
        });
        data.brands = resourceModels.Brand.query(function (results) {
            data.models = resourceModels.Model.query(function (results) {
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