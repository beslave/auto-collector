'use strict';

var STORE_KEY = 'listFilters';

module.exports = function ($scope, $rootScope, $filter, $resource, store, autoData) {
    autoData.filters = store.get(STORE_KEY) || {};
    $scope.autoData = autoData;

    var originalYearFrom = autoData.filters.yearFrom,
        originalYearTo = autoData.filters.yearTo;

    $scope.updateFilters = function (sender) {
        if (sender == 'yearFrom') {
            originalYearFrom = autoData.filters.yearFrom;

            autoData.filters.yearTo = originalYearTo;
            if (originalYearFrom && originalYearTo && originalYearTo < originalYearFrom) {
                autoData.filters.yearTo = autoData.filters.yearFrom;
            }
        }
        if (sender == 'yearTo') {
            originalYearTo = autoData.filters.yearTo;

            autoData.filters.yearFrom = originalYearFrom;
            if (originalYearFrom && originalYearTo && originalYearTo < originalYearFrom) {
                autoData.filters.yearFrom = originalYearTo;
            }
        }

        store.set(STORE_KEY, autoData.filters);
        $rootScope.$broadcast('autoDataChanged', autoData);
    };

    var updateModelsList = function () {
        $scope.models = $filter('filter')($scope.autoData.models, {
            brand: autoData.filters.brand
        });
        if ($scope.models.length === 1) {
            autoData.filters.model = $scope.models[0];
        }
    };

    $scope.$watch(function () {
        return autoData.filters.brand;
    }, updateModelsList);
    $scope.$on('autoDataChanged', updateModelsList);

    setTimeout($scope.updateFilters, 0);
};