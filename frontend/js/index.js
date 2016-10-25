'use strict';

require('angular-storage');

var app = require('./app.js');
var controllers = require('./controllers');
var providers = require('./providers');

app.provider('autoData', providers.autoData);

app.controller('ItemsListController', controllers.ItemsListController);
app.controller('ItemsListFiltersController', controllers.ItemsListFiltersController);
app.controller('ModelController', controllers.ModelController);

app.config(function ($routeProvider, $locationProvider, $sceDelegateProvider) {
    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        window.settings.templatesURL + '**'
    ]);
    $routeProvider.when('/:modelId/', {
        templateUrl: window.settings.templatesURL + 'model.html',
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
