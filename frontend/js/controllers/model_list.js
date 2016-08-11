'use strict';

module.exports = function ($scope, $http, $window) {
    var container = document.getElementById('js-models-list');
    var page = 0;
    var lastPage = page;
    var apiUrlTpl = container.dataset.apiUrl;
    var isEnd = false;
    var scrollThreshold = 250;

    $scope.models = [];
    $scope.filterParams = {};

    function loadExtraModels () {
        var modelElements = document.querySelectorAll('.model');
        var lastModelElement = modelElements[modelElements.length - 1];
        var bottom = lastModelElement && lastModelElement.getBoundingClientRect().bottom;
        if (isEnd || bottom - window.innerHeight > scrollThreshold) {
            return;
        }

        lastPage += 1;
        $http({
            method: 'GET',
            url: apiUrlTpl.replace('{page}', lastPage)
        }).then(function (response) {
            var extraModels = response.data;
            Array.prototype.push.apply($scope.models, extraModels);
            isEnd = extraModels.length === 0;
            setTimeout(loadExtraModels, 0);
        });
    }

    $scope.$on('modelListFiltersChange', function (e, filters) {
        $scope.filterParams = {};

        if (filters.brand) {
            $scope.filterParams.brand = filters.brand.name;
        }

        if (filters.model) {
            $scope.filterParams.id = filters.model.id;
        }

        setTimeout(loadExtraModels, 0);
    });

    setTimeout(function () {
        loadExtraModels();
        angular.element($window).bind('scroll', loadExtraModels);
    }, 0);
};