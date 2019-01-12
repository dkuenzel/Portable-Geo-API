jQuery(function() {
	jQuery('.ss_button').on('click',function() {
		jQuery('.ss_content').slideUp('fast');
		content = jQuery(this).next('.ss_content');
		if (content.is(":hidden")) {
			jQuery(this).next('.ss_content').slideDown('fast');
		}
	});
});
