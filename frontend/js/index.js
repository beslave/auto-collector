'use strict';

require('angular-storage');

var app = require('./app');
var controllers = require('./controllers');
var providers = require('./providers');

app.provider('autoData', providers.autoData);
app.factory('resourceModels', providers.resourceModels);

Object.keys(controllers).forEach(function (controllerName) {
    app.controller(controllerName, controllers[controllerName]);
});

app.config(function ($resourceProvider, $routeProvider, $locationProvider, $sceDelegateProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $routeProvider.when('/compare/', {
        templateUrl: window.settings.templatesURL + 'compare.html'
    });
    $routeProvider.when('/:modelId/', {
        templateUrl: window.settings.templatesURL + 'model.html',
        controller: 'ModelController'
    });
    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        window.settings.templatesURL + '**'
    ]);

    $locationProvider.html5Mode(true);
});

app.run(function ($rootScope) {
    $rootScope.$on('$routeChangeSuccess', function (e, current) {
        var isModalPath = current && current.originalPath !== '/';

        angular.element(document.body).toggleClass('modal-open', isModalPath);
    });
});
