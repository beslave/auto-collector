'use strict';

var utils = require('../utils');

module.exports = function ($scope, $http, $filter, $window, $location, autoData) {
    var advertisements = [];
    var PER_PAGE = 20;
    var SCROLL_THRESHOLD = 250;
    var number = $filter('number');

    $scope.items = [];
    $scope.filteredItems = [];
    $scope.limitedItems = [];
    $scope.showItemsCount = PER_PAGE;

    var avg = function (values) {
        return values.reduce(function(a, b) {
            return a + b;
        }, 0) / values.length;
    };
    var getGroupKey = function (adv) {
        return adv.model_id;
    };
    var isSatisfyFilters = function (adv) {
        var model = autoData.getModel(adv.model_id);
        var brand = model && autoData.getBrand(model.brand_id);
        var brandId = brand && brand.id;
        var filterBrandId = autoData.filters.brand && autoData.filters.brand.id;
        var filterModelId = autoData.filters.model && autoData.filters.model.id;

        if (!autoData.filters.isNew && adv.is_new) {
            return false;
        }
        if (!autoData.filters.isUsed && !adv.is_new) {
            return false;
        }
        if (autoData.filters.yearFrom && adv.year < autoData.filters.yearFrom) {
            return false;
        }
        if (autoData.filters.yearTo && adv.year > autoData.filters.yearTo) {
            return false;
        }
        if (autoData.filters.brand && !angular.equals(filterBrandId, brandId)) {
            return false;
        }
        if (autoData.filters.model && !angular.equals(filterModelId, adv.model_id)) {
            return false;
        }
        return true;
    };

    var updateItems = function () {
        var grouped_items = {};
        advertisements.forEach(function (adv) {
            if (!isSatisfyFilters(adv)) {
                return;
            }

            var key = getGroupKey(adv);
            if (!grouped_items[key]) {
                grouped_items[key] = {
                    'model_id': adv.model_id,
                    'previews': [],
                    'prices': [],
                }
            }
            grouped_items[key].prices.push(adv.price);

            if (adv.preview) {
                grouped_items[key].previews.push(adv.preview);
            }
        });

        $scope.items = [];
        angular.forEach(grouped_items, function (item) {
            item.price_avg = avg(item.prices);
            item.price_min = Math.min.apply(null, item.prices)
            item.price_max = Math.max.apply(null, item.prices);
            item.preview = item.previews[0];
            item.model = autoData.getModel(item.model_id);
            item.brand = item.model && autoData.getBrand(item.model.brand_id)
            
            item.price = number(item.price_avg, 0);
            if (item.price_min !== item.price_max) {
                item.price += ' (' + number(item.price_min, 0) + ' - ' + number(item.price_max, 0) + ')';
            }
            item.price += ' грн.';

            if (item.brand && item.model) {
                item.title = item.brand.name + ' ' + item.model.name;
            }
            item.url = '/' + item.model_id + '/';

            $scope.items.push(item);
        });

        $scope.filteredItems = $filter('orderBy')($scope.items, 'price_avg');
        $scope.limitedItems = $filter('limitTo')($scope.filteredItems, $scope.showItemsCount);

        loadExtraItems();
        $scope.$applyAsync();
    };

    var loadExtraItems = utils.debounce(function () {
        if ($scope.showItemsCount >= $scope.filteredItems.length) {
            return;
        }

        var itemElements = document.querySelectorAll('.js-list-item');
        var lastItemElement = itemElements[itemElements.length - 1];
        var bottom = lastItemElement && lastItemElement.getBoundingClientRect().bottom;
        if (bottom - window.innerHeight < SCROLL_THRESHOLD) {
            $scope.showItemsCount += PER_PAGE;
            $scope.limitedItems = $filter('limitTo')($scope.filteredItems, $scope.showItemsCount);
            $scope.$applyAsync();
            loadExtraItems();
        }
    }, 0);

    function resetItems() {
        $scope.showItemsCount = PER_PAGE;

        updateItems();
    }
    $scope.$on('autoDataChanged', resetItems);
    $http.get('/api').then(function (response) {
        var fields = response.data.fields;
        advertisements = response.data.rows.map(function (row) {
            var adv = {};
            row.forEach(function (value, i) {
                adv[fields[i]] = value;
            });
            adv.preview = '/advertisement/' + adv.id + '/preview/'
            return adv;
        });
        resetItems();
    });

    loadExtraItems();
    angular.element($window).bind('scroll', loadExtraItems);
};