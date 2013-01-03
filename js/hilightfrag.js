// Highlight the blog entry named by the fragment.
// Ned Batchelder.

jQuery(function($){
	var frag = location.hash;
	if (frag.length > 1 && frag != '#commentform' && frag != '#comments') {
		$(frag).addClass('hilitefragment');
	}
});

// Manipulate the submit button on the comment form.
jQuery(function($){
    // Make the add button wait 2 secs to really submit.
    $("#addbtn").click(function(){
        $.timer(2000, function(timer){
            $("#addbtn").unbind().click();
            timer.stop();
        });
        return false;
    });
    // In 2 seconds, 
    $.timer(2000, function(timer) {
        // remove our custom click function.
        $("#addbtn").unbind();
        timer.stop();
    });
});
