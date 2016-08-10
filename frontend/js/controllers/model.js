'use strict';

module.exports = function ($scope, $http, $location) {
    angular.element(document.body).addClass('modal-open');
    $http.get($location.absUrl()).then(function(response) {
        var data = response.data;
        $scope.brand = data.brand;
        $scope.model = data.model;
        $scope.advertisements = data.advertisements;
    });
};