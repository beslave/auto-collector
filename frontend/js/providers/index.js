exports.autoData = function () {
    var data = {
        brands: [],
        models: [],
        filters: [],

        getBrand: function (brandId) {
            if (this.brands) {
                return this.brands.filter(function (brand) {
                    return brand.id === brandId;
                })[0];
            }
        },
        getModel: function (modelId) {
            if (this.models) {
                return this.models.filter(function (model) {
                    return model.id === modelId;
                })[0];
            }
        }
    };

    this.$get = function ($rootScope, $resource) {
        var Brand = $resource('/api/brands/:brandId', {brandId: '@id'});
        var Model = $resource('/api/models/:modelId', {modelId: '@id'});
        data.brands = Brand.query(function (results) {
            data.models = Model.query(function (results) {
                data.models.forEach(function (model) {
                    model.brand = data.getBrand(model.brand_id);
                });
                $rootScope.$broadcast('autoDataChanged', data);
            });
        });
        return data;
    };
};