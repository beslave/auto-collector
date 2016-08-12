'use strict';

module.exports = function ($scope, $rootScope, $resource, autoData) {
    $scope.filters = {};
    $scope.brands = autoData.brands;
    $scope.models = [];

    var originalYearFrom = null,
        originalYearTo = null;

    $scope.filterByBrand = function () {
        $scope.models = autoData.models.filter(function (model) {
            return $scope.filters.brand && model.brand_id === $scope.filters.brand.id;
        });

        if ($scope.models.length === 1) {
            $scope.filters.model = $scope.models[0];
        }

        $scope.updateFilters();
    };

    $scope.updateFilters = function (sender) {
        if (sender == 'yearFrom') {
            originalYearFrom = $scope.filters.yearFrom;

            $scope.filters.yearTo = originalYearTo;
            if (originalYearFrom && originalYearTo && originalYearTo < originalYearFrom) {
                $scope.filters.yearTo = $scope.filters.yearFrom;
            }
        }
        if (sender == 'yearTo') {
            originalYearTo = $scope.filters.yearTo;

            $scope.filters.yearFrom = originalYearFrom;
            if (originalYearFrom && originalYearTo && originalYearTo < originalYearFrom) {
                $scope.filters.yearFrom = originalYearTo;
            }
        }
        $rootScope.$broadcast('itemsListFiltersChange', $scope.filters);
    };
};