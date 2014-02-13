var active_detectors = ["D01", "D07"];
var selected_detectors = ["D01"];
var old_selected_detectors = [];

function zeroPad(num, places) {
	var zero = places - num.toString().length + 1;
	return Array(+(zero > 0 && zero)).join("0") + num;
}

function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

var toggle_button_state = function (self)
{
	if (hasClass(self, 'btn-primary')){ // Not Selected
		self.className = "btn btn-success btn-xs";
		var index = selected_detectors.indexOf(self.id);
		if (index == -1){
			selected_detectors.push(self.id);
			$(document.body).trigger('DetButtons:selection', [self.id]);
		}
	}
	else {
		if (selected_detectors.length > 1){
			self.className = "btn btn-primary btn-xs";
			var index = selected_detectors.indexOf(self.id);
			if (index > -1) {
	    		selected_detectors.splice(index, 1);
	    		$(document.body).trigger('DetButtons:deselection', [self.id])
			}
		}
	}
}

var update_active_detectors = function (){
	for (var i=1;i<71;i++)
	{ 
		d3.select("#D"+zeroPad(i,2)).classed("disabled", function(){
			return (active_detectors.indexOf("D"+zeroPad(i,2))==-1);
		});
	}
}

var select_all = function(){
	old_selected_detectors = selected_detectors;
	selected_detectors = active_detectors;
}

var deslect_all = function(){
	if (old_selected_detectors.length>0){
		selected_detectors = old_selected_detectors;
	}
	else {
		selected_detectors = [active_detectors[0]];
	}
}

var update_selected_detectors = function (){
	for (var i = selected_detectors.length - 1; i >= 0; i--) {
		document.getElementById(selected_detectors[i]).className = "btn btn-success btn-xs";
	};
}

var _init_buttons = function() {
	active_detectors = [];
	selected_detectors = [];
	for (var i = 0; i < data['scan_dets'].length; i++) {
		active_detectors.push(data['scan_dets'][i]);
	};
	selected_detectors.push(data['scan_dets'][0]);
	update_active_detectors();
	update_selected_detectors();
}

$(document).ready(function(){
	try {
		_init_buttons();
	}
	catch(err) {
		console.log('Unable to init detector buttons');
	}
	

	$(document.body).on('Scan:begin', function(event, new_data) {
		active_detectors = [];
    	selected_detectors = [];
    	for (var i = 0; i < new_data['scan_dets'].length; i++) {
    		active_detectors.push(new_data['scan_dets'][i]);
    	};
    	selected_detectors.push(new_data['scan_dets'][0]);
    	update_active_detectors();
		update_selected_detectors();
	});
	$(document.body).on('Scan:reply', function(event, new_data) {
		active_detectors = [];
    	selected_detectors = [];
    	for (var i = 0; i < new_data['scan_dets'].length; i++) {
    		active_detectors.push(new_data['scan_dets'][i]);
    	};
    	selected_detectors.push(new_data['scan_dets'][0]);
    	update_active_detectors();
		update_selected_detectors();
	});
})


