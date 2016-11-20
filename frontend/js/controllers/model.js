'use strict';

var Panel = require('../utils/panel');

var TABLE_ORDERING_STORE_KEY = 'advertisements-table-ordering';

module.exports = function ($scope, $filter, $location, $routeParams, store, autoData, resourceModels) {
    angular.element(document.body).addClass('modal-open');
    $scope.advertisements = [];
    $scope.filteredAdvertisements = [];

    $scope.panels = [
        new Panel('Кузов', {
            body_type: 'Тип кузова',
            doors: 'Кількість дверей',
            seats: 'Кількість місць'
        }),
        new Panel('Габарити та маса ', {
            length: 'Довжина, мм',
            width: 'Ширина, мм',
            height: 'Висота, мм',
            clearance: 'Кліренс, кг',
            curb_weight: 'Споряджена маса, кг',
            max_allowed_weight: 'Макс. допустима маса, кг',
            trunk_volume: 'Об\'єм багажника, л',
            fuel_tank_volume: 'Об\'єм паливного бака, л',
            wheel_base: 'Колісна база, мм',
            bearing_capacity: 'Вантажопідйомність, кг'
        }),
        new Panel('Двигун', {
            engine_position: 'Положення',
            energy_source: 'Паливо',
            engine_volume: 'Об\'єм, см3',
            engine_cylinders: 'Кількість циліндрів',
            engine_cylinders_position: 'Розташування циліндрів',
            engine_horses: 'Потужність, к.с',
            // engine_rotations_start: '',
            // engine_rotations_end: '',
            engine_max_torque: 'Макс. обертальний момент, Н*м',
            // engine_max_torque_rotations_start: '',
            // engine_max_torque_rotations_end: '',
            engine_fuel_rate_mixed: 'Витрата пального (змішаний цикл) л/100км',
            engine_fuel_rate_urban: 'Витрата пального (міський цикл) л/100км',
            engine_fuel_rate_extra_urban: 'Витрата пального (приміський цикл) л/100км',
            engine_valves_count: 'Кількість клапанів',
            // @TODO: 'Наявність компресора',
            engine_co2_emission: 'Викид CO2, г/км',
            engine_euro_toxicity_norms: 'Норми токсичностi EURO'
        }),
        new Panel('Трансмісія', {
            gearbox_type: 'Коробка передач',
            gears_count: 'Кількість передач',
            drive_type: 'Тип приводу'
        }),
        new Panel('Кермо', {
            steer_amplifier: 'Підсилювач керма',
            spread_diameter: 'Діаметр розвороту, м'
        }),
        new Panel('Динамічні характеристики', {
            max_velocity: 'Максимальна швидкість, км/год',
            acceleration_time_to_100: 'Час розгону до 100 км/год, мс'  // @TODO: Convert to seconds
        })
    ];

    $scope.bodyTypes = [];
    $scope.doorsCountList = [];
    $scope.seatsCountList = [];

    $scope.model = resourceModels.Model.get({modelId: $routeParams.modelId}, function (model) {
        $scope.advertisements = model.advertisements;

        var bodyTypesIndex = {};
        var doorsCountListIndex = {};
        var seatsCountListIndex = {};

        angular.forEach($scope.advertisements, function (advertisement) {
            angular.forEach($scope.panels, function (panel) {
                panel.populateData(advertisement);
            });
        });

        updateFilters();
    });

    $scope.ordering = store.get(TABLE_ORDERING_STORE_KEY) || {
        by: 'price',
        reverse: false
    };

    $scope.setOrderBy = function(attr) {
        if ($scope.ordering.by === attr) {
            $scope.ordering.reverse = !$scope.ordering.reverse;
        } else {
            $scope.ordering.by = attr;
            $scope.ordering.reverse = false;
        }
        store.set(TABLE_ORDERING_STORE_KEY, $scope.ordering);
    };

    $scope.closeModal = function () {
        $location.path('/');
    };

    $scope.getAdvertisementUrl = function (adv) {
        return '/advertisement/' + adv.id + '/go/';
    };

    function updateFilters () {
        var filtered = $scope.advertisements;

        if (!autoData.filters.isNew) {
            filtered = $filter('filter')(filtered, {is_new: false});
        }

        if (!autoData.filters.isUsed) {
            filtered = $filter('filter')(filtered, {is_new: true});
        }

        if (autoData.filters.bodyType) {
            filtered = $filter('filter')(filtered, {
                body_type_id: autoData.filters.bodyType.id
            });
        }

        if (autoData.filters.yearFrom) {
            filtered = filtered.filter(function (adv) {
                return adv.year >= autoData.filters.yearFrom;
            });
        }

        if (autoData.filters.yearTo) {
            filtered = filtered.filter(function (adv) {
                return adv.year <= autoData.filters.yearTo;
            });
        }

        $scope.filteredAdvertisements = filtered;
        $scope.$applyAsync();
    }

    $scope.$on('autoDataChanged', updateFilters);
    updateFilters();
};