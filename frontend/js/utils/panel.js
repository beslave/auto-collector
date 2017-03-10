module.exports = function (title, fields, ids) {
    var dataStorage = {};
    var filteredDataStorage = {};

    this.title = title;
    this.fields = [];
    this.isExpanded = true;

    this.ids = ids || [];

    this.populateData = function (data, itemId) {
        dataStorage[itemId].push(data);
    };

    this.getItemFilteredData = function (itemId) {
        return filteredDataStorage[itemId];
    };

    this.applyFilters = function (filters) {
        this.itemPreviews = [];

        this.fields.forEach(function (field) {
            field.items.forEach(function (item) {
                item.valuesList = [];
                item.valuesIndex = {};
            });
        });

        angular.forEach(dataStorage, function (dataList, itemId) {
            var itemTitle = 'testTitle';
            var itemPreview = null;

            filteredDataStorage[itemId] = [];

            dataList.forEach(function (data) {
                if (!filters.isNew && data.is_new === true) {
                    return;
                }
                if (!filters.isUsed && data.is_new === false) {
                    return;
                }

                if (filters.yearFrom && filters.yearFrom > data.year) {
                    return;
                }

                if (filters.yearTo && filters.yearTo < data.year) {
                    return;
                }

                if (filters.energySource && filters.energySource.id !== data.energy_source_id) {
                    return;
                }

                if (filters.bodyType && filters.bodyType.id !== data.body_type_id) {
                    return;
                }

                filteredDataStorage[itemId].push(data);

                this.fields.forEach(function (field) {
                    var item = field.itemsIndex[itemId];
                    var value = data[field.field];

                    if (field.converter) {
                        value = field.converter(value);
                    }

                    if (value == null || value in item.valuesIndex) {
                        return;
                    }

                    item.valuesIndex[value] = true;
                    item.valuesList.push(value);
                });
            }, this);
        }, this);
    };

    this.visible = function () {
        return this.fields.reduce(function (isPanelVisible, field) {
            return isPanelVisible || field.visible();
        }, false);
    };

    this.toggleExpand = function () {
        this.isExpanded = !this.isExpanded;
    };

    this.ids.forEach(function (id) {
        dataStorage[id] = [];
        filteredDataStorage[id] = [];
    });

    var sortingFunc = function (a, b) {
        if (a > b) return 1;
        if (a < b) return -1;
        return 0;
    };

    angular.forEach(fields, function (fieldOptions, field) {
        if (angular.isString(fieldOptions)) {
            fieldOptions = {
                title: fieldOptions
            };
        }

        var field = {
            field: field,
            title: fieldOptions.title,
            converter: fieldOptions.converter,
            items: this.ids.map(function (id) {
                return {
                    id: id,
                    valuesList: [],
                    valuesIndex: {},

                    visible: function () {
                        return this.valuesList.length > 0;
                    },
                    getValuesListRange: function () {
                        var sortedValues = this.valuesList.slice().sort(sortingFunc);
                        var lastIndex = sortedValues.length - 1;

                        return '' + sortedValues[0] + ' - ' + sortedValues[lastIndex];
                    }
                };
            }),
            itemsIndex: {},

            first: function () {
                return this.items[0];
            },
            visible: function () {
                return this.items.reduce(function (isFieldVisible, item) {
                    return isFieldVisible || item.visible();
                }, false);
            }
        };
        field.items.forEach(function (item) {
            field.itemsIndex[item.id] = item;
        });

        this.fields.push(field);
    }, this);
};
