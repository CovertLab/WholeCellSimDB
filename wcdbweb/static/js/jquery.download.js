jQuery.download = function(url, data, method){
    var form = $('<form action="'+ url +'" method="'+ (method||'post') +'"></form>');
    
	for (var key in data) {
		var input = $('<input type="hidden" name="'+ key +'" />').appendTo(form); 
        input.val(data[key]);
	}
    
    form.appendTo('body').submit().remove();
};