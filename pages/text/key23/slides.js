function make_slides_static() {
    $('.incremental').removeClass('incremental');
    $('.later').removeClass('later');
}

$(function() {
    if ($("body.slides").length) {
        // Visit this_file.html?showall to see all the incremental stuff at once...
        var showall = (window.location.href.indexOf("showall") !== -1);
        if (showall) {
            make_slides_static();
        }

        $(".slide").slippy({
            // settings go here
            // possible values are:
            //  - animLen, duration for default animations (0 = disabled)
            //  - animInForward, receives a slide and animates it
            //  - animInRewind, receives a slide and animates it
            //  - animOutForward, receives a slide and animates it
            //  - animOutRewind, receives a slide and animates it
            //  - baseWidth, defines the base for img resizing, if you don't want only
            //    full-width images, specify this as the pixel width of a slide so that
            //    images are scaled properly (default is 620px wide)
            //  - ratio, defines the width/height ratio of the slides, defaults to 1.3 (620x476)
            //  - margin, the fraction of screen to use as slide margin, defaults to 0.15
            ratio: 16/9,
            margin: 0,
            baseWidth: false,   // disable all active image resizing
            incrementalBefore: function (el) {
                var $el = $(el);
                if ($el.hasClass("disp-none")) {
                    // The scrolling chat slides need this.
                    $el.css({ display: "none" });
                }
                else {
                    $el.css({ opacity: 0.01 });
                }
                $el.addClass("incrhidden");
            },
            incrementalAfter: function (el) {
                var $el = $(el);
                var $slide = $el.closest(".slide");
                $slide.find(".thendim:not(.incrhidden)").css({ opacity: .5 });
                if ($el.hasClass("disp-none")) {
                    $el.css({ display: "block" });
                }
                if ($el.hasClass("fadein")) {
                    $el.animate({ opacity: 1 }, $el.data("timein") || 650);
                }
                else {
                    $el.css({ opacity: 1 });
                }
                var show_selector = $el.data("show");
                if (show_selector) {
                    $slide.find(show_selector).show();
                }
                $el.removeClass("incrhidden");
            },
            animInForward: function (slide) {
                var slide = $(slide);
                if (slide.hasClass("fadein")) {
                    slide.css('opacity', '0').css('left', '50%').animate({opacity: '1'}, 150);
                }
                else {
                    slide.css('left', '150%').animate({left: '50%'}, 350);
                }
                slide.find(".incremental").css({opacity:0});    // IDK why this hides them, but 0.01 does not.
            },
            animOutForward: function (slide) {
                var slide = $(slide);
                if (slide.hasClass("fadeout")) {
                    slide.animate({opacity: '1'}, 150).animate({left: '-50%'}, 0);
                }
                else {
                    slide.animate({left: '-50%'}, 350);
                }
            }
        });
    }

    // Highlight the code in <pre> blocks.
    $('pre').each(function (i, e) {
        hljs.highlightBlock(e, '    ');
    });

    // Highlight.js doesn't make "self" special, so we do it ourselves.
    $('pre').each(function (i, e) {
        var $e = $(e);
        $e.html($e.html().replace(/\bself\b/g, '<span class="self">self</span>'));
    });

    // Convert <pre> to have <span class='line'> for each line.
    $('pre').each(function (i, e) {
        var $e = $(e);
        var lines = $e.html().split("\n");
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (line === "") {
                lines[i] = "<span class='blankline'>&nbsp;</span>";
            }
            else {
                lines[i] = "<span class='line'>" + lines[i] + "</span>";
            }
        }
        $e.html(lines.join("\n"));
    });

    $("div.slide").lineselect({ lines: "pre span.line" });

    // Pre-select lines based on a select= attribute.
    $('pre').each(function (i, e) {
        var $e = $(e);
        var select = $e.attr("select");
        if (select) {
            $e.lineselect(select);
        }
    });

    // Make all the English text look nicer.
    $('h1, h2, h3, li, p').each(function (i, e) {
        var $e = $(e);
        $e.html(typogr.typogrify($e));
    });
});
