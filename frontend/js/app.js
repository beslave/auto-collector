'use strict';

var app = angular.module('autoCollectorApp', ['ngResource', 'ngRoute']);
app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
}]);

module.exports = app;