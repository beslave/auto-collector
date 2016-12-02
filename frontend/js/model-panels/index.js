var Panel = require('../utils/panel');

function dividerConverter (divider) {
    return function (value) {
        return value && (value / divider);
    };
}

function roman(value) {
    var ROMAN_SYMBOLS = {
        1: 'I',
        2: 'II',
        3: 'III',
        4: 'IV',
        5: 'V',
        6: 'VI',
        7: 'VII',
        8: 'VIII',
        9: 'IX',
        10: 'X',
    }
    return ROMAN_SYMBOLS[value];
}

exports.getPanels = function (ids) {
    return [
        new Panel('Загальне', {
            price: 'Ціна, грн',
            year: 'Рік випуску',
        }, ids),
        new Panel('Кузов', {
            body_type: 'Тип кузова',
            doors: 'Кількість дверей',
            seats: 'Кількість місць'
        }, ids),
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
        }, ids),
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
            engine_fuel_rate_mixed: {
                title: 'Витрата пального (змішаний цикл) л/100км',
                converter: dividerConverter(1000)
            },
            engine_fuel_rate_urban: {
                title: 'Витрата пального (міський цикл) л/100км',
                converter: dividerConverter(1000)
            },
            engine_fuel_rate_extra_urban: {
                title: 'Витрата пального (приміський цикл) л/100км',
                converter: dividerConverter(1000)
            },
            engine_valves_count: 'Кількість клапанів',
            // @TODO: 'Наявність компресора',
            engine_co2_emission: 'Викид CO2, г/км',
            engine_euro_toxicity_norms: {
                title: 'Норми токсичностi EURO',
                converter: roman
            }
        }, ids),
        new Panel('Трансмісія', {
            gearbox_type: 'Коробка передач',
            gears_count: 'Кількість передач',
            drive_type: 'Тип приводу'
        }, ids),
        new Panel('Кермо', {
            steer_amplifier: 'Підсилювач керма',
            spread_diameter: {
                title: 'Діаметр розвороту, м',
                converter: dividerConverter(100),
            }
        }, ids),
        new Panel('Динамічні характеристики', {
            max_velocity: 'Максимальна швидкість, км/год',
            acceleration_time_to_100: {
                title: 'Час розгону до 100 км/год, с',
                converter: dividerConverter(1000),
            }
        }, ids)
    ];
};

exports.withFullfilledPanels = function (ids, resourceModel, callback) {
    var singleItemModel = !angular.isArray(ids)

    if (singleItemModel) {
        ids = [ids];
    }

    var dataIndex = {};
    var panels = exports.getPanels(ids);
    var loadedModelsCount = 0;


    var callCallbackWithData = function () {
        var modelsData;

        if (singleItemModel) {
            var id = ids[0];
            modelsData = dataIndex[id];
        } else {
            modelsData = ids.map(function (id) {
                return dataIndex[id];
            });
        }

        return callback(modelsData, panels);
    };

    ids.forEach(function (id) {
        resourceModel.get({modelId: id}, function (model) {
            var data = {
                'model': model,
                'advertisements': model.advertisements,
            }
            dataIndex[id] = data;

            angular.forEach(data.advertisements, function (advertisement) {
                angular.forEach(panels, function (panel) {
                    panel.populateData(advertisement, id);
                });
            });

            loadedModelsCount++;

            if (loadedModelsCount === ids.length) {
                callCallbackWithData();
            }
        });
    });
}
