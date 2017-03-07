'use strict';

var modelPanels = require('../model-panels');

var STORE_KEY = 'compared-items';

module.exports = function ($scope, store, autoData, resourceModels) {
    var comparedIndex = {};
    var comparedCache = {};

    $scope.compared = store.get(STORE_KEY) || [];
    $scope.comparePanels = [];
    $scope.compareTitles = [];
    $scope.comparePreviews = [];

    $scope.inComparison = function (key) {
        return comparedIndex[key];
    };

    $scope.toggleCompareState = function (key, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        if ($scope.inComparison(key)) {
            var deleteItemIndex = $scope.compared.indexOf(key);
            $scope.compared.splice(deleteItemIndex, 1);
        } else {
            $scope.compared.push(key);
        }

        update();
    };

    $scope.getComparedItemsCount = function () {
        return $scope.compared.length;
    };

    $scope.getModelTitle = function (modelId) {
        var data = comparedCache[modelId];
        return data && (data.model.brand.name + ' ' + data.model.name);
    };

    $scope.getModelPreview = function (modelId) {
        var data = comparedCache[modelId];
        return data && (data.advertisement && data.advertisement.preview);
    };

    $scope.getModelUrl = function (modelId) {
        return '/' + modelId + '/';
    };

    function updateFilters () {
        $scope.comparePanels.forEach(function (panel) {
            panel.applyFilters(autoData.filters);
        });
    }

    function update () {
        comparedCache = {};
        comparedIndex = {};
        $scope.compared.forEach(function (key) {
            comparedIndex[key] = true;
        });
        store.set(STORE_KEY, $scope.compared);

        modelPanels.withFullfilledPanels($scope.compared, resourceModels.Model, function (modelsData, panels) {
            $scope.comparedModelsData = modelsData;
            $scope.comparePanels = panels;

            updateFilters();

            $scope.compared.forEach(function (modelId) {
                var model = autoData.getModel(modelId);
                var advertisement = $scope.comparePanels[0].getItemFilteredData(modelId)[0];

                if (model) {
                    comparedCache[modelId] = {
                        model: model,
                        advertisement: advertisement
                    };
                }
            });

            $scope.$applyAsync();
        });
    }

    $scope.$on('autoDataChanged', update);
};