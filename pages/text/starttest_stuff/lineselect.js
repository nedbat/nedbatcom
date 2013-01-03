/**
 * Lineselect jQuery plugin
 *
 * Make containers of lines show selection line-by-line.
 * Good for highlighting lines of code.
 * 
 * Not ready as a general-purpose plugin!  active_sel
 * and sub_sel are particular to Slippy.
 *
 * Ned Batchelder
 * Copyright 2011
 * @license MIT License
 */
(function ($) {
    var container_class = "lineselectable";
    var focus_class = "focus";
    var container_sel = "." + container_class;
    var active_sel = ".slide.active";
    var sub_sel = "div.line";

    var select_line = function (container, line, single) {
        if (single) {
            container.find(sub_sel).removeClass("selected");
        }
        line.addClass("selected");
        line.trigger("lineselected");
    };

    var select_line_by_number = function (container, lineno, single) {
        select_line(container, container.find(sub_sel + ":nth-child(" + lineno + ")"), single);
    };

    var keydown_fn = function (e) {
        // Find the one container to manipulate.
        var container = $(active_sel + " " + container_sel + "." + focus_class + ":visible");
        if (container.length === 0) {
            container = $(active_sel + " " + container_sel + ":visible");
        }
        if (container.length !== 1) {
            return;
        }

        var the_selected = container.find(sub_sel + ".selected"), 
            selected = 0;
        if (the_selected.length) {
            selected = container.find(sub_sel).length - the_selected.nextAll().length;
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

        if (selected < 1 || selected > container.find(sub_sel).length) {
            return;
        }
        select_line_by_number(container, selected, true);
    };

    var make_line_selectable = function (elements) {
        if (keydown_fn) {
            $(document).keydown(keydown_fn);
            keydown_fn = null;
        }
        return elements.each(function () {
            var container = $(this);
            container.addClass(container_class);
            container.find(sub_sel).live('click',
                function (e) { 
                    select_line(container, $(this), !e.ctrlKey);
                }
            );
        });
    };

    $.fn.lineselect = function (lineno) {
        if (lineno === undefined) {
            // Make elements line-selectable
            make_line_selectable(this);
        } 
        else {
            return this.each(function () {
                select_line_by_number($(this), lineno, true);
            });
        }
    };

}(jQuery));

