module.exports = function (title, fields) {
    this.title = title;
    this.fields = [];
    this.isExpanded = true;

    this.populateData = function (data) {
        angular.forEach(this.fields, function (field) {
            var value = data[field.field];

            if (field.converter) {
                value = field.converter(value);
            }

            if (value == null || value in field.valuesIndex) {
                return;
            }

            field.valuesIndex[value] = true;
            field.valuesList.push(value);
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

    angular.forEach(fields, function (fieldOptions, field) {
        if (angular.isString(fieldOptions)) {
            fieldOptions = {
                title: fieldOptions
            };
        }

        this.push({
            field: field,
            title: fieldOptions.title,
            converter: fieldOptions.converter,
            valuesList: [],
            valuesIndex: {},

            visible: function () {
                return this.valuesList.length > 0;
            }
        });
    }, this.fields);
};
