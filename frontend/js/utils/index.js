'use strict';

exports.debounce = function (fn, delay) {
    var timeoutId;
    return function () {
        var context = this;
        var args = arguments;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(function () {
            return fn.apply(context, args);
        }, delay);
    };
};
