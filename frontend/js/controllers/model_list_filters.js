'use strict';

module.exports = function ($scope, $rootScope, $resource) {
    var Brand = $resource('/api/brands/:brandId', {brandId: '@id'});
    var Model = $resource('/api/brands/:brandId/:modelId/models', {modelId: '@id'});
    $scope.filters = {};

    $scope.brands = Brand.query(function (data) {
        $scope.brands = data;
    });
    $scope.models = [];

    $scope.filterByBrand = function () {
        $scope.models = [];

        if ($scope.filters.brand) {
            $scope.models = Model.query({
                brandId: $scope.filters.brand.id
            }, function (models) {
                $scope.models = models;
            });
        }

        $scope.updateFilters();
    };

    $scope.updateFilters = function () {
        $rootScope.$broadcast('modelListFiltersChange', $scope.filters);
    };
};