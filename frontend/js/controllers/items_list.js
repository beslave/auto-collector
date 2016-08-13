'use strict';

module.exports = function ($scope, $http, $filter, $window, autoData) {
    var advertisements = [];
    var filterParams = {};
    var PER_PAGE = 20;
    var SCROLL_THRESHOLD = 250;

    $scope.items = [];
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
        if (filterParams.yearFrom && adv.year < filterParams.yearFrom) {
            return false;
        }
        if (filterParams.yearTo && adv.year > filterParams.yearTo) {
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
        Object.keys(grouped_items).forEach(function (key) {
            var number = $filter('number');
            var item = grouped_items[key];
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
    };

    var loadExtraItems = function (timeout) {
        setTimeout(function () {
            if ($scope.showItemsCount >= $scope.items.length) {
                return;
            }

            var itemElements = document.querySelectorAll('.js-list-item');
            var lastItemElement = itemElements[itemElements.length - 1];
            var bottom = lastItemElement && lastItemElement.getBoundingClientRect().bottom;
            if (bottom - window.innerHeight < SCROLL_THRESHOLD) {
                $scope.showItemsCount += PER_PAGE;
                $scope.$applyAsync();
                loadExtraItems(500);
            }
        }, timeout || 0);
    };

    $http.get('/').then(function (response) {
        var fields = response.data.fields;
        advertisements = response.data.rows.map(function (row) {
            var adv = {};
            row.forEach(function (value, i) {
                adv[fields[i]] = value;
            });
            return adv;
        });
        updateItems();
    });

    $scope.$on('itemsListFiltersChange', function (e, filters) {
        filterParams = filters;
        $scope.showItemsCount = PER_PAGE;

        updateItems();
        loadExtraItems();
    });

    loadExtraItems();
    angular.element($window).bind('scroll', loadExtraItems);
};