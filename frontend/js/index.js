'use strict';

require('angular-storage');

var app = require('./app');
var controllers = require('./controllers');
var providers = require('./providers');

app.provider('autoData', providers.autoData);
app.factory('resourceModels', providers.resourceModels);

app.controller('ItemsListController', controllers.ItemsListController);
app.controller('ItemsListFiltersController', controllers.ItemsListFiltersController);
app.controller('ModelController', controllers.ModelController);

app.config(function ($resourceProvider, $routeProvider, $locationProvider, $sceDelegateProvider) {
    $resourceProvider.defaults.stripTrailingSlashes = false;
    $routeProvider.when('/:modelId/', {
        templateUrl: window.settings.templatesURL + 'model.html',
        controller: 'ModelController'
    });
    $sceDelegateProvider.resourceUrlWhitelist([
        'self',
        window.settings.templatesURL + '**'
    ]);

    // configure html5 to get links working on jsfiddle
    $locationProvider.html5Mode(true);
});

app.run(function ($rootScope) {
    $rootScope.$on('$routeChangeStart', function () {
        angular.element(document.body).removeClass('modal-open');
    });
});
