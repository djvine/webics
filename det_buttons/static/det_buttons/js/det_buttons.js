active_detectors = ["D01", "D07"];
selected_detectors = ["D01"];

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

var update_selected_detectors = function (){
	for (var i = selected_detectors.length - 1; i >= 0; i--) {
		document.getElementById(selected_detectors[i]).className = "btn btn-success btn-xs";
	};
}

var _init_buttons = function() {
	update_active_detectors();
	update_selected_detectors();
}

$(document).ready(function(){
	_init_buttons();

	$(document.body).on('DetButtons:selection', function(event, param) {
    	console.log('A button selected '+ param);
	});
	$(document.body).on('DetButtons:deselection', function(event, param) {
    	console.log('A button was deselected '+ param);
	});
})


