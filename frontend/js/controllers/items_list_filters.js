'use strict';

var STORE_KEY = 'listFilters';

module.exports = function ($scope, $rootScope, $filter, $resource, store, autoData) {
    autoData.filters = store.get(STORE_KEY) || {
        bodyType: null,
        brand: null,
        yearFrom: null,
        yearTo: null,
        isNew: true,
        isUsed: true,
    };
    $scope.autoData = autoData;

    var originalYearFrom = autoData.filters.yearFrom,
        originalYearTo = autoData.filters.yearTo;

    $scope.updateFilters = function (sender) {
        var not_new_not_used = !autoData.filters.isNew && !autoData.filters.isUsed;

        if (sender == 'isNew' && not_new_not_used) {
            autoData.filters.isUsed = true;
        }
        if (sender == 'isUsed' && not_new_not_used) {
            autoData.filters.isNew = true;
        }

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

    setTimeout($scope.updateFilters, 0);
};