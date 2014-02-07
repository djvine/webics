var data1 = [];
var l1 = [];

var _init_lineplots = function({
	// Get initial data
	$(document).trigger("LinePlots:initial", [beamline])
})



$(document).ready(function(){
	_init_lineplots();

	$(document.body).on('Scan:reply', function(event, param) {
    	console.log('Got scan reply');
    	data1 = param;
    	var l1 = new LinePlot({containerId: 'line_plot', data: data1});
	});
})