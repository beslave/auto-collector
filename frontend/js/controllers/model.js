'use strict';

var TABLE_ORDERING_STORE_KEY = 'advertisements-table-ordering';

module.exports = function ($scope, $filter, $http, $location, store, autoData) {
    angular.element(document.body).addClass('modal-open');
    $scope.advertisements = [];
    $scope.filteredAdvertisements = [];

    $http.get($location.absUrl()).then(function(response) {
        var data = response.data;
        $scope.brand = data.brand;
        $scope.model = data.model;
        $scope.advertisements = data.advertisements;
        updateFilters();
    });

    $scope.ordering = store.get(TABLE_ORDERING_STORE_KEY) || {
        by: 'price',
        reverse: false
    };

    $scope.setOrderBy = function(attr) {
        if ($scope.ordering.by === attr) {
            $scope.ordering.reverse = !$scope.ordering.reverse;
        } else {
            $scope.ordering.by = attr;
            $scope.ordering.reverse = false;
        }
        store.set(TABLE_ORDERING_STORE_KEY, $scope.ordering);
    };

    $scope.closeModal = function () {
        $location.path('/');
    };

    function updateFilters () {
        var filtered = $scope.advertisements;

        if (!autoData.filters.isNew) {
            filtered = $filter('filter')(filtered, {is_new: false});
        }

        if (!autoData.filters.isUsed) {
            filtered = $filter('filter')(filtered, {is_new: true});
        }

        if (autoData.filters.yearFrom) {
            filtered = filtered.filter(function (adv) {
                return adv.year >= autoData.filters.yearFrom;
            });
        }

        if (autoData.filters.yearTo) {
            filtered = filtered.filter(function (adv) {
                return adv.year <= autoData.filters.yearTo;
            });
        }

        $scope.filteredAdvertisements = filtered;
        $scope.$applyAsync();
    }

    $scope.$on('autoDataChanged', updateFilters);
    updateFilters();
};