$(function() {
    if ($("body.slides").length) {
        // Visit this_file.html?showall to see all the incremental stuff at once...
        var showall = (window.location.href.indexOf("showall") !== -1);
        if (showall) {
            $('.incremental').each(function (i, e) {
                $(e).removeClass('incremental');
            });
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
            margin: 0.01,
            baseWidth: false,   // disable all active image resizing
            incrementalBefore: function (el) {
                $(el).css({ opacity: 0.01 });
            },
            incrementalAfter: function (el) {
                var $el = $(el);
                if ($el.hasClass("fadein")) {
                    $el.animate({opacity: '1'}, $el.data("timein") || 650);
                }
                else {
                    $el.css({ opacity: 1 });
                }
            },
            animInForward: function (slide) {
                var slide = $(slide);
                if (slide.hasClass("fadein")) {
                    slide.css('opacity', '0').css('left', '50%').animate({opacity: '1'}, 650);
                }
                else {
                    slide.css('left', '150%').animate({left: '50%'}, 350);
                }
                slide.find(".incremental").css({opacity:0});    // IDK why this hides them, but 0.01 does not.
            },
            animOutForward: function(slide) {
                var slide = $(slide);
                if (slide.hasClass("fadeout")) {
                    slide.animate({opacity: '1'}, 650).animate({left: '-50%'}, 0);
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
