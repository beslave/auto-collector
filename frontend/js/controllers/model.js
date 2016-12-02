'use strict';

var modelPanels = require('../model-panels');

var TABLE_ORDERING_STORE_KEY = 'advertisements-table-ordering';

module.exports = function ($scope, $filter, $routeParams, store, autoData, resourceModels) {
    $scope.advertisements = [];
    $scope.filteredAdvertisements = [];

    $scope.panels = [];
    $scope.model = null;

    modelPanels.withFullfilledPanels($routeParams.modelId, resourceModels.Model, function (modelData, panels) {
        $scope.model = modelData.model;
        $scope.advertisements = modelData.advertisements;
        $scope.panels = panels;
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

    $scope.getAdvertisementUrl = function (adv) {
        return '/advertisement/' + adv.id + '/go/';
    };

    function updateFilters () {
        var filtered = $scope.advertisements;

        if (!autoData.filters.isNew) {
            filtered = $filter('filter')(filtered, {is_new: false});
        }

        if (!autoData.filters.isUsed) {
            filtered = $filter('filter')(filtered, {is_new: true});
        }

        if (autoData.filters.bodyType) {
            filtered = $filter('filter')(filtered, {
                body_type_id: autoData.filters.bodyType.id
            });
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

        $scope.panels.forEach(function (panel) {
            panel.applyFilters(autoData.filters);
        });
        $scope.$applyAsync();
    }

    $scope.$on('autoDataChanged', updateFilters);
    updateFilters();
};