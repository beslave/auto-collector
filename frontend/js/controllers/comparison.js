'use strict';

var modelPanels = require('../model-panels');

var STORE_KEY = 'compared-items';

module.exports = function ($scope, store, autoData, resourceModels) {
    var compared = store.get(STORE_KEY) || [];
    var comparedIndex = {};

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
            var deleteItemIndex = compared.indexOf(key);
            compared.splice(deleteItemIndex, 1);
        } else {
            compared.push(key);
        }

        update();
    };

    $scope.getComparedItemsCount = function () {
        return compared.length;
    };

    function updateFilters () {
        $scope.comparePanels.forEach(function (panel) {
            panel.applyFilters(autoData.filters);
        });
    }

    function update () {
        comparedIndex = {};
        compared.forEach(function (key) {
            comparedIndex[key] = true;
        });
        store.set(STORE_KEY, compared);

        modelPanels.withFullfilledPanels(compared, resourceModels.Model, function (modelsData, panels) {
            $scope.comparedModelsData = modelsData;
            $scope.comparePanels = panels;

            updateFilters();

            $scope.compareTitles = [];
            $scope.comparePreviews = [];

            compared.forEach(function (modelId) {
                var model = autoData.getModel(modelId);
                var advertisement = $scope.comparePanels[0].getItemFilteredData(modelId)[0];

                if (!model) {
                    return modelId;
                }

                $scope.compareTitles.push(model.brand.name + ' ' + model.name);
                $scope.comparePreviews.push(advertisement && advertisement.preview);
            });

            $scope.$applyAsync();
        });
    }

    $scope.$on('autoDataChanged', update);
};