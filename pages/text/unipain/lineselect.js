/**
 * Lineselect jQuery plugin
 *
 * Make containers of lines show selection line-by-line.
 * Good for highlighting lines of code.
 * 
 * Ned Batchelder
 * Copyright 2011
 * @license MIT License
 */
(function ($) {
    // Internal constants
    var container_class = "_lineselect_container";
    var sub_class = "_lineselect_sub";
    
    // Global options
    var options = {
        focus: ".focus",
        active_sel: ".slide.active"
    };

    var select_line = function (container, line, single) {
        if (single) {
            container.find("."+sub_class).removeClass("selected");
        }
        line.addClass("selected");
        line.trigger("lineselected");
    };

    var select_line_by_number = function (container, lineno, single) {
        select_line(container, container.find("."+sub_class + ":eq(" + (lineno-1) + ")"), single);
    };

    var keydown_fn = function (e) {
        // Find the one container to manipulate.
        var container = $(options.active_sel + " ." + container_class + options.focus_class + ":visible");
        if (container.length === 0) {
            container = $(options.active_sel + " ." + container_class + ":visible");
        }
        if (container.length !== 1) {
            return;
        }

        var the_selected = container.find("."+sub_class + ".selected"), 
            selected = 0;
        if (the_selected.length) {
            var total_lines = container.find("."+sub_class).length;
            var following_lines = the_selected.nextAll("."+sub_class).length;
            selected = total_lines - following_lines;
        }

        switch (e.keyCode) {
        case 71:    // G
            selected = 1;
            break;

        case 74:    // J
            selected += 1;
            break;

        case 75:    // K
            selected -= 1;
            break;

        default:
            //console.log('down: ' + e.keyCode);
            return;
        }

        if (selected < 1 || selected > container.find("."+sub_class).length) {
            return;
        }
        select_line_by_number(container, selected, true);
    };

    var make_line_selectable = function (elements, opts) {
        // Register a document keydown function once.
        if (keydown_fn) {
            $(document).keydown(keydown_fn);
            keydown_fn = null;
        }
        // Apply the options, some are global.
        $.extend(options, opts);

        // In every container, find all the "lines", mark them, and give them
        // click handlers.
        return elements.each(function () {
            var container = $(this);
            container.addClass(container_class);
            container.find(opts.lines)
                .addClass(sub_class)
                .live('click',
                    function (e) { 
                        select_line(container, $(this), !e.ctrlKey);
                    }
                );
        });
    };

    $.fn.lineselect = function (arg) {
        if (typeof arg === "number") {
            this.each(function () {
                select_line_by_number($(this), lineno, true);
            });
        }
        else {
            // Make elements line-selectable
            make_line_selectable(this, arg);
        } 
        return this;
    };

}(jQuery));

