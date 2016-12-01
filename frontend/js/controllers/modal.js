'use strict';

module.exports = function ($scope, $location) {
    $scope.closeModal = function () {
        $location.path('/');
    };
};