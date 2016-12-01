'use strict';

var STORE_KEY = 'compared-items';

module.exports = function ($scope, store) {
    var compared = store.get(STORE_KEY) || [];
    var comparedIndex;

    var save = function () {
        comparedIndex = {};
        compared.forEach(function (key) {
            comparedIndex[key] = true;
        });
        store.set(STORE_KEY, compared);
    }

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

        save();
    };
    save();
};