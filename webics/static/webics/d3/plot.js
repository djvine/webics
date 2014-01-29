var n_xticks = 10;
var yScale = 'linear'; // can be pow, log, linear
var scales = [['linear','Linear'], ['pow','Power'], ['log','Log']];
var margin = {top: 20, right: 30, bottom: 20, left: 30}


function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

var selected_buttons = [];
var active_buttons = [];

function toggle_state(button_id)
{
	if (hasClass(document.getElementById(button_id), 'btn-primary')){ // Not Selected
		document.getElementById(button_id).className = "btn btn-success btn-xs";
		var index = selected_buttons.indexOf(button_id);
		if (index == -1){
			selected_buttons.push(button_id);
		}
	}
	else {
		if (selected_buttons.length > 1){
			document.getElementById(button_id).className = "btn btn-primary btn-xs";
			var index = selected_buttons.indexOf(button_id);
			if (index > -1) {
	    		selected_buttons.splice(index, 1);
			}
		}
	}
	console.log(selected_buttons);
	ch.updateData(dataset)
}

detector_color_map = [
	{"D00": "acqua"}, {"D01": "acquamarine"}, {"D02": "black"}, {"D03": "blue"}, {"D04": "blueviolet"}, 
	{"D05": "brown"}, {"D06": "cadetblue"}, {"D07": "chatreuse"}, {"D08": "chocolate"}, {"D09": "coral"}, 
	{"D10": "cornflowerblue"}, {"D11": "crimson"}, {"D12": "cyan"}, {"D13": "darkblue"}, {"D14": "darkcyan"}, 
	{"D15": "darkgoldenrod"}, {"D16": "darkgray"}, {"D17": "darkgreen"}, {"D18": "darkmagenta"}, {"D19": "darkolivegreen"}, 
	{"D20": "darkorange"}, {"D21": "darkorchid"}, {"D22": "darkred"}, {"D23": "darkslateblue"}, {"D24": "darkslategray"}, 
	{"D25": "firebrick"}, {"D26": "forestgreen"}, {"D27": "fuchsia"}, {"D28": "gold"}, {"D29": "green"}, 
	{"D30": "hotpink"}, 	{"D31": "goldenrod"}, {"D32": "gray"}, {"D33": "greenyellow"}, {"D34": "indianred"}, 
	{"D35": "indigo"}, {"D36": "lawngreen"}, {"D37": "lightblue"}, {"D38": "lightcoral"}, {"D39": "lightgreen"}, 
	{"D40": "lightpink"}, {"D41": "lightsalmon"}, {"D42": "lightseagreen"}, {"D43": "lightskyblue"}, {"D44": "lightslategray"}, 
	{"D45": "lime"}, {"D46": "magenta"}, {"D47": "maroon"}, {"D48": "mediumblue"}, {"D49": "mediumorchid"}, 
	{"D50": "navy"}, {"D51": "olive"}, {"D52": "olivedrab"}, {"D53": "orange"}, {"D54": "orangered"}, 
	{"D55": "orchid"}, {"D56": "palegreen"}, {"D57": "palevioletred"}, {"D58": "peru"}, {"D59": "purple"}, 
	{"D60": "red"}, {"D61": "royalblue"}, {"D62": "saddlebrown"}, {"D63": "seagreen"}, {"D64": "slateblue"}, 
	{"D65": "slategray"}, {"D66": "yellow"}, {"D67": "teal"}, {"D68": "tomato"}, {"D69": "violet"}
]

dataset = [
			{"y": 0.7190236397473576, "x": 0, "name": "D01"}, 
			{"y": 0.024750818605637326, "x": 0, "name": "D05"}, 
			{"y": 0.10365829809519755, "x": 0, "name": "D10"}, 
			{"y": 0.6290133137904929, "x": 1, "name": "D01"}, 
			{"y": 0.08630600550904954, "x": 1, "name": "D05"}, 
			{"y": 0.3541530982686767, "x": 1, "name": "D10"}, 
			{"y": 0.9517491888699899, "x": 2, "name": "D01"}, 
			{"y": 0.7505306465025037, "x": 2, "name": "D05"}, 
			{"y": 0.29114701091200024, "x": 2, "name": "D10"}, 
			{"y": 0.20160074198876288, "x": 3, "name": "D01"}, 
			{"y": 0.67850809035152, "x": 3, "name": "D05"}, 
			{"y": 0.04420952913710252, "x": 3, "name": "D10"}, 
			{"y": 0.5825103897868874, "x": 4, "name": "D01"}, 
			{"y": 0.4830402065690812, "x": 4, "name": "D05"}, 
			{"y": 0.37378730731733356, "x": 4, "name": "D10"}, 
			{"y": 0.1345441758661805, "x": 5, "name": "D01"}, 
			{"y": 0.5581186383345774, "x": 5, "name": "D05"}, 
			{"y": 0.3937908204469104, "x": 5, "name": "D10"}, 
			{"y": 0.07844805073432193, "x": 6, "name": "D01"}, 
			{"y": 0.5084864869817969, "x": 6, "name": "D05"}, 
			{"y": 0.25366694254980515, "x": 6, "name": "D10"}, 
			{"y": 0.10176417224548084, "x": 7, "name": "D01"}, 
			{"y": 0.2432423435661042, "x": 7, "name": "D05"}, 
			{"y": 0.602471438697417, "x": 7, "name": "D10"}, 
			{"y": 0.053703931139014616, "x": 8, "name": "D01"}, 
			{"y": 0.06135187906671724, "x": 8, "name": "D05"}, 
			{"y": 0.16349870217979567, "x": 8, "name": "D10"}, 
			{"y": 0.0897347858412737, "x": 9, "name": "D01"}, 
			{"y": 0.961627306750081, "x": 9, "name": "D05"}, 
			{"y": 0.7732018327413872, "x": 9, "name": "D10"}
		]

newdataset = [
				{"y": 0.7146504601983563, "x": 0, "name": "D01"}, 
				{"y": 0.8741497797762526, "x": 0, "name": "D05"}, 
				{"y": 0.8515481260527834, "x": 0, "name": "D10"}, 
				{"y": 0.45303544525031114, "x": 1, "name": "D01"}, 
				{"y": 0.33243530643918784, "x": 1, "name": "D05"}, 
				{"y": 0.34740946003449724, "x": 1, "name": "D10"}, 
				{"y": 0.49704788975482284, "x": 2, "name": "D01"}, 
				{"y": 0.6556723864982885, "x": 2, "name": "D05"}, 
				{"y": 0.530745148518531, "x": 2, "name": "D10"}, 
				{"y": 0.011249670353936425, "x": 3, "name": "D01"}, 
				{"y": 0.5843044435074304, "x": 3, "name": "D05"}, 
				{"y": 0.5545008770818121, "x": 3, "name": "D10"}, 
				{"y": 0.34595059649872995, "x": 4, "name": "D01"}, 
				{"y": 0.7044284084643396, "x": 4, "name": "D05"}, 
				{"y": 0.4258036248060423, "x": 4, "name": "D10"}, 
				{"y": 0.11979719965242752, "x": 5, "name": "D01"}, 
				{"y": 0.8506008491966667, "x": 5, "name": "D05"}, 
				{"y": 0.9740670401480455, "x": 5, "name": "D10"}, 
				{"y": 0.4196760460716351, "x": 6, "name": "D01"}, 
				{"y": 0.6596477072009489, "x": 6, "name": "D05"}, 
				{"y": 0.21949094995181528, "x": 6, "name": "D10"}, 
				{"y": 0.960115797655491, "x": 7, "name": "D01"}, 
				{"y": 0.508594815391405, "x": 7, "name": "D05"}, 
				{"y": 0.48691137328626866, "x": 7, "name": "D10"}, 
				{"y": 0.336178496489451, "x": 8, "name": "D01"}, 
				{"y": 0.5490181734346192, "x": 8, "name": "D05"}, 
				{"y": 0.5304398976346045, "x": 8, "name": "D10"}, 
				{"y": 0.09276671237153933, "x": 9, "name": "D01"}, 
				{"y": 0.32790963388506655, "x": 9, "name": "D05"}, 
				{"y": 0.9380127114885172, "x": 9, "name": "D10"}
			]


dataset = dataset.map( function (d) { 
    return { 
      name: d['name'],   // the + sign will coerce strings to number values
      x: d['x'],
      y: d['y'] 
  	}; 
});   

dataset = d3.nest().key(function(d) { return d.name; }).entries(dataset	);

newdataset = newdataset.map( function (d) { 
    return { 
      name: d['name'],   // the + sign will coerce strings to number values
      x: d['x'],
      y: d['y'] 
  	}; 
});   

newdataset = d3.nest().key(function(d) { return d.name; }).entries(newdataset);

var createChart = function(data, container, margin){
	var w=$(container).width();
	var h=400;
	var tickFormatForLogScale = ",.01f";
	var width = w - margin.left - margin.right;
	var height = h - margin.top - margin.bottom;
	var transitionDuration = 300;

	var xScale = d3.scale.linear()
	                     .range([margin.left, w-margin.right])
	                     .domain([
	                     	d3.min(dataset, function(d) { return d3.min(d.values, function (d) { return d.x; }); }), 
		           			d3.max(dataset, function(d) { return d3.max(d.values, function (d) { return d.x; }); })
		           		 ])
		           		 .nice();

	var yLeft = d3.scale.linear()
	                     .range([margin.bottom, h-margin.top])
	                     .domain([
	                     	d3.max(dataset, function(d) { return d3.max(d.values, function (d) { return d.y; }); }), 
		           			d3.min(dataset, function(d) { return d3.min(d.values, function (d) { return d.y; }); })
		           		  ])
	                     .nice();

	var color = d3.scale.category10()
	    .domain(d3.keys(dataset[0]).filter(function(key) { return key === "key"; }));

	var xAxis = d3.svg.axis()
	    .scale(xScale)
	    .orient("bottom")
	    .ticks(n_xticks)
	    .tickSubdivide(1);

	var yAxis = d3.svg.axis()
	    .scale(yLeft)
	    .orient("left")
	    .ticks(5);

	var line = d3.svg.line()
	    .interpolate("")
	    .x(function(d) { return xScale(d.x); })
	    .y(function(d) { return yLeft(d.y); });

	var svg = d3.select("#chart").append("svg")
	    .attr("width", w + margin.left + margin.right)
	    .attr("height", h + margin.top + margin.bottom)
	    .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	svg.append("g")
	    .attr("class", "axis")  //Assign "axis" class
	    .attr("id", "xaxis") 
	    .attr("transform", "translate(0," + (h - margin.bottom) + ")")
	    .call(xAxis);

	svg.append("g")
	    .attr("class", "axis")  //Assign "axis" class
	    .attr("id", "yaxis")
	    .attr("transform", "translate(" + margin.left + ",0)")
	    .call(yAxis);

	var scans = svg.selectAll(".scan")
	      .data(dataset, function(d) { return d.key; })
	      .enter().append("g")
	      .attr("class", "scan")
	      .append("path")
	      .attr("class", "line")
	      .attr("d", function(d) { return line(d.values); })
	      .style("stroke", function(d) { return color(d.key); })
	      .style("fill","None");

	svg.append("text")
	    .attr("class", "xlabel")
	    .attr("text-anchor", "end")
	    .attr("x", 2*margin.left)
	    .attr("y", height+55)
	    .text("X Label");

	svg.selectAll("line.verticalGrid").data(xScale.ticks(n_xticks)).enter()
	    .append("line")
	        .attr(
	        {
	            "class":"verticalGrid",
	            "x1" : function(d){ return xScale(d);},
	            "x2" : function(d){ return xScale(d);},
	            "y1" : height,
	            "y2" : 0,
	            "fill" : "none",
	            "shape-rendering" : "crispEdges",
	            "stroke" : "gray",
	            "stroke-width" : "1px",
	            "opacity":0.5
	        });

	var xlabelGroup = svg.append("svg:g")
			.attr("class", "x-label-group")
			.append("svg:text")
			.attr("class", "x-label")
			.attr("id", "x-label-id")
			.attr("text-anchor", "end")
			.attr("opacity", "0.75") 
			.attr("font-size", "11")
			.attr("y", -4)
			.attr("x", w-margin.right)
			.text('NA')

	function zeroPad(num, places) {
	  var zero = places - num.toString().length + 1;
	  return Array(+(zero > 0 && zero)).join("0") + num;
	}

	this.update_active_detectors = function(data){

		selected_buttons = [];
		for (var i=0;i<70;i++)
		{ 
			document.getElementById("D"+zeroPad(i,2)).className = "btn btn-primary btn-xs disabled";
		}
		
		data.forEach(function(element, index, array){
			if (index==0){
				document.getElementById(element.key).className = "btn btn-success btn-xs";
				selected_buttons.push(element.key);
			}
			else {
				document.getElementById(element.key).className = "btn btn-primary btn-xs";
			}
		})
	}

	this.updateData = function(data) {
		
		//update active buttons
		//update_active_detectors(data);
		g_scan = document.getElementsByClassName('scan');
		for (var i = 0; i < g_scan.length; i++) {
			g_scan[i].parentElement.removeChild(g_scan[i]);
		};
		//d3.selectAll(".scan").remove()
		
		svg.selectAll(".scan")
	      .data(data, function(d) { return d.key; })
	      .enter()
	      .append("g")
	      .filter(function(d) { return (selected_buttons.indexOf(d.key) != -1) })
	      .attr("class", "scan")
	      .append("path")
	      .attr("class", "line")
	      .attr("d", function(d) { return line(d.values); })
	      .style("stroke", function(d) { return color(d.key); })
	      .style("fill","None");
	    
		// redraw (with transition)
		redrawAxes(true, data);
		

		
		// fire an event that data was updated
		//$(container).trigger('LineGraph:dataModification')
	}

	var createScaleButtons = function() {
		var cumulativeWidth = 0;		
		// append a group to contain all lines
		var buttonGroup = svg.append("svg:g")
				.attr("class", "scale-button-group")
			.selectAll("g")
				.data(scales)
			.enter().append("g")
				.attr("class", "scale-buttons")
			.append("svg:text")
				.attr("class", "scale-button")
				.text(function(d, i) {
					return d[1];
				})
				.attr("font-size", "12") // this must be before "x" which dynamically determines width
				.attr("fill", function(d) {
					if(d[0] == yScale) {
						return "black";
					} else {
						return "blue";
					}
				})
				.classed("selected", function(d) {
					if(d[0] == yScale) {
						return true;
					} else {
						return false;
					}
				})
				.attr("x", function(d, i) {
					// return it at the width of previous labels (where the last one ends)
					var returnX = cumulativeWidth;
					// increment cumulative to include this one
					cumulativeWidth += this.getComputedTextLength()+5;
					return returnX;
				})
				.attr("y", -4)
				.on('click', function(d, i) {
					handleMouseClickScaleButton(this, d, i);
				});
	}

	var handleMouseClickScaleButton = function(button, buttonData, index) {
			if(index == 0) {
				switchToLinearScale();
			} else if(index == 1) {
				switchToPowerScale();
			} else if(index == 2) {
				switchToLogScale();
			}
			
			// change text decoration
			svg.selectAll('.scale-button')
			.attr("fill", function(d) {
				if(d[0] == yScale) {
					return "black";
				} else {
					return "blue";
				}
			})
			.classed("selected", function(d) {
				if(d[0] == yScale) {
					return true;
				} else {
					return false;
				}
			})
			
		}

	var switchToPowerScale = function() {
		yScale = 'pow';
		redrawAxes(true);
		redrawLines(true);
		
		// fire an event that config was changed
		$(svg).trigger('LineGraph:configModification')
	}

	var switchToLogScale = function() {
		yScale = 'log';
		redrawAxes(true);
		redrawLines(true);
		
		// fire an event that config was changed
		$(svg).trigger('LineGraph:configModification')
	}

	var switchToLinearScale = function() {
		yScale = 'linear';
		redrawAxes(true);		
		redrawLines(true);
		
		// fire an event that config was changed
		$(svg).trigger('LineGraph:configModification')
	}

	var redrawAxes = function(withTransition, data) {
		initY(data);
		initX(data);
		if(withTransition) {
			// slide x-axis to updated location
			svg.selectAll("g #xaxis.axis").transition()
			.duration(transitionDuration)
			.ease("linear")
			.call(xAxis)				  
		
			// slide y-axis to updated location
			svg.selectAll("g #yaxis.axis").transition()
			.duration(transitionDuration)
			.ease("linear")
			.call(yAxisLeft)
			
		} else {
			// slide x-axis to updated location
			graph.selectAll("g #xaxis.axis")
			.call(xAxis)				  
		
			// slide y-axis to updated location
			graph.selectAll("g #yaxis.left")
			.call(yAxisLeft)
		}
	}
	
	var redrawLines = function(withTransition) {
		/**
		* This is a hack to deal with the left/right axis.
		*
		* See createGraph for a larger comment explaining this. 
		*
		* Yes, it's ugly. If you can suggest a better solution please do.
		*/
		
		// redraw lines
		if(withTransition) {
			svg.selectAll("path.line")
			.transition()
				.duration(transitionDuration)
				.ease("linear")
				.attr("d", function(d) { return line(d.values); })
				.attr("transform", null);
		} else {
			svg.selectAll("path.line")
				.attr("d", function(d) { return line(d.values); })
				.attr("transform", null);
		}
	}

	
	/*
	 * Allow re-initializing the y function at any time.
	 *  - it will properly determine what scale is being used based on last user choice (via public switchScale methods)
	 */
	var initY = function(data) {

		var numAxisLabels = 6;
		var numAxisLabelsPowerScale = 6;
		var numAxisLabelsLinearScale = 10;
		var d_min = 0.;
		var d_max = 0.;
		for (var i = 0; i<data.length; i++) {
			for (var j = 0;  j< data[i].values.length; j++) {
				if (i==0){
					var d_min = data[i].values[j].y;
					var d_max = data[i].values[j].y;
				}
				else {
					if (data[i].values[j].y<d_min){
						d_min = data[i].values[j].y;
					}
					if (data[i].values[j].y>d_max){
						d_max = data[i].values[j].y;
					}
				}
			};
		};
		if (d_min==d_max){
			d_min--;
			d_max++;
		}

		if(yScale == 'pow') {
			yLeft = d3.scale.pow()
					.exponent(0.3)
					.domain([d_max. d_min])
					.range([margin.bottom, h-margin.top])
					.nice();	
			numAxisLabels = numAxisLabelsPowerScale;
		} else if(yScale == 'log') {
			// we can't have 0 so will represent 0 with a very small number
			// 0.1 works to represent 0, 0.01 breaks the tickFormatter
			yLeft = d3.scale.log()
				.domain([d_max, d_min])
				.range([margin.bottom, h-margin.top])
				.nice();	
		} else if(yScale == 'linear') {
			yLeft = d3.scale.linear()
			.domain([d_max, d_min])
			.range([margin.bottom, h-margin.top])
			.nice();
			numAxisLabels = numAxisLabelsLinearScale;
		}

		yAxisLeft = d3.svg.axis().scale(yLeft)
					.ticks(numAxisLabels, tickFormatForLogScale)
					.orient("left");

	}

	
	/*
	 * Allow re-initializing the x function at any time.
	 */
	var initX = function(data) {
		// X scale starts at epoch time 1335035400000, ends at 1335294600000 with 300s increments
		xScale = d3.scale.linear()
                     .range([margin.left, w-margin.right])
                     .domain([
                     	d3.min(data, function(d) { return d3.min(d.values, function (d) { return d.x; }); }), 
	           			d3.max(data, function(d) { return d3.max(d.values, function (d) { return d.x; }); })
	           			])
                     .nice();

		// create yAxis (with ticks)
		xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(n_xticks).tickSubdivide(1);
	}
	this.getScale = function() {
		return yScale;
	}

	createScaleButtons();

	var hoverlineXoffset = margin.left+15;
	// Hover line. 
	var hoverLineGroup = svg.append("g")
						.attr("class", "hover-line");
	var hoverLine = hoverLineGroup
		.append("line")
			.attr("x1", 10).attr("x2", 10) 
			.attr("y1", 0).attr("y2", h); 
	// Hide hover line by default.
	hoverLine.style("opacity", 1e-6);
	var xlabelFormat = d3.format(",.01f");
	// Add mouseover events.
	d3.select("#chart")
		.on("mouseover", function() { 
	  		//console.log('mouseover');
		})
		.on("mousemove", function() {
	  		//console.log('mousemove', d3.mouse(this));
	  		var x = d3.mouse(this)[0]-hoverlineXoffset;
	  		hoverLine.attr("x1", x).attr("x2", x).style("opacity", 1);
	  		xlabelGroup.text(xlabelFormat(xScale.invert(x)));
	  	})  
	  	.on("mouseout", function() {
	    	//console.log('mouseout');
	    	hoverLine.style("opacity", 1e-6);
	  	});
}

ch = new createChart(dataset, "#chart", margin);
/*
current_dataset = 0;
setInterval(function() {
		if (current_dataset==0){
			ch.updateData(newdataset);
			current_dataset=1;
		}
		else {
			ch.updateData(dataset);
			current_dataset=0;
		}
	}, 2500);
*/
$( document ).ready(function() {
   	ch.update_active_detectors(dataset);
   	ch.updateData(dataset);
});





