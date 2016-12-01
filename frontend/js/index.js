'use strict';

require('angular-storage');

var app = require('./app');
var controllers = require('./controllers');
var providers = require('./providers');

app.provider('autoData', providers.autoData);
app.factory('resourceModels', providers.resourceModels);

app.controller('ComparisonController', controllers.ComparisonController);
app.controller('ItemsListController', controllers.ItemsListController);
app.controller('ItemsListFiltersController', controllers.ItemsListFiltersController);
app.controller('ModalController', controllers.ModalController);
app.controller('ModelController', controllers.ModelController);

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

    // configure html5 to get links working on jsfiddle
    $locationProvider.html5Mode(true);
});

app.run(function ($rootScope) {
    $rootScope.$on('$routeChangeSuccess', function (e, current) {
        var isModalPath = current && current.originalPath !== '/';

        angular.element(document.body).toggleClass('modal-open', isModalPath);
    });
});
