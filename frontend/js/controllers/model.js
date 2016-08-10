'use strict';

module.exports = function ($scope, $http, $location) {
    $http.get($location.absUrl()).then(function(response) {
        $scope.model = response.data;
    });
};