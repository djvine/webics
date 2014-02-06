active_detectors = ["D01", "D07"];
selected_detectors = ["D01"];

function zeroPad(num, places) {
	var zero = places - num.toString().length + 1;
	return Array(+(zero > 0 && zero)).join("0") + num;
}

var toggle_button_state = function (button_id)
{
	d3.select("#"+button_id).classed("btn-success", function(d, i){
		if (this.className.indexOf('btn-success')==-1){
			if (selected_detectors.indexOf(this.id)==-1){
				selected_detectors.push(this.id)
			}
			console.log(selected_detectors);
			return true
		} else {
			if (selected_detectors.length>1){
				if (selected_detectors.indexOf(this.id)>-1){
					selected_detectors.splice(selected_detectors.indexOf(this.id), 1)
				}
			}
			console.log(selected_detectors);
			return false;
		}

	})
}

var update_active_detectors = function (){
	for (var i=1;i<71;i++)
	{ 
		d3.select("#D"+zeroPad(i,2)).classed("disabled", function(){
			return (active_detectors.indexOf("D"+zeroPad(i,2))==-1);
		});
	}
}

var _init_buttons = function() {
	update_active_detectors();
}

$(document).ready(function(){
	_init_buttons();
})
