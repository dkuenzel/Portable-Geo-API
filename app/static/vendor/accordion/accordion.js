jQuery(function() {
	jQuery('.ss_button').on('click',function() {
		content = jQuery(this).next('.ss_content');
		if (content.is(":hidden")) {
			jQuery(this).next('.ss_content').slideDown('fast');
		}
		else {
			jQuery(this).next('.ss_content').slideUp('fast');
		}
	});
});
