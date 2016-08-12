'use strict';

module.exports = function ($scope, $rootScope, $resource, autoData) {
    $scope.filters = {};
    $scope.brands = autoData.brands;
    $scope.models = [];

    $scope.filterByBrand = function () {
        $scope.models = autoData.models.filter(function (model) {
            return $scope.filters.brand && model.brand_id === $scope.filters.brand.id;
        });

        if ($scope.models.length === 1) {
            $scope.filters.model = $scope.models[0];
        }

        $scope.updateFilters();
    };

    $scope.updateFilters = function () {
        $rootScope.$broadcast('itemsListFiltersChange', $scope.filters);
    };
};