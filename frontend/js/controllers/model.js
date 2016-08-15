'use strict';

var TABLE_ORDERING_STORE_KEY = 'advertisements-table-ordering';

module.exports = function ($scope, $http, $location, store) {
    angular.element(document.body).addClass('modal-open');

    $http.get($location.absUrl()).then(function(response) {
        var data = response.data;
        $scope.brand = data.brand;
        $scope.model = data.model;
        $scope.advertisements = data.advertisements;
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
};