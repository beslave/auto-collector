'use strict';

var app = require('./app.js');
var controllers = require('./controllers');

app.controller('ModelListController', controllers.ModelListController);
app.controller('ModelController', controllers.ModelController);

app.config(function ($routeProvider, $locationProvider) {
    $routeProvider
    .when('/:modelId/', {
        templateUrl: '/static/templates/model.html',
        controller: 'ModelController'
    });

    // configure html5 to get links working on jsfiddle
    $locationProvider.html5Mode(true);
});

app.run(function ($rootScope) {
    $rootScope.$on('$routeChangeStart', function () {
        angular.element(document.body).removeClass('modal-open');
    });
});
