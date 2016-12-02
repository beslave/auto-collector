module.exports = function () {
    var data = {
        advertisements: [],
        advertisementsPrimaryIndex: {},
        bodyTypes: [],
        bodyTypesWithAdvertisements: [],
        bodyTypesPrimaryIndex: {},
        brands: [],
        brandsPrimaryIndex: {},
        models: [],
        modelsPrimaryIndex: {},
        filters: [],

        getAdvertisement: function (advertisementId) {
            return this.advertisementsPrimaryIndex[advertisementId];
        },
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

    this.$get = function ($http, $rootScope, $resource, resourceModels) {
        $http.get('/api/').then(function (response) {
            var fields = response.data.fields;
            data.advertisements = response.data.rows.map(function (row) {
                var adv = {};
                row.forEach(function (value, i) {
                    adv[fields[i]] = value;
                });
                adv.preview = '/advertisement/' + adv.id + '/preview/'

                data.advertisementsPrimaryIndex[adv.id] = adv;

                return adv;
            });
            $rootScope.$broadcast('autoDataChanged', data);
        });
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