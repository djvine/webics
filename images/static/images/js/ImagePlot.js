/**
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 /*
 	Author: B.J. Christensen
	Adapted By: D.J. Vine (djvine@gmail.com)
 */


function ImagePlot(argsMap){

	/* *************************************************************** */
	/* public methods */
	/* *************************************************************** */
	var self = this;

	this.updateData = function(newData) {
		// Get detector to plot
		
		det = getRequiredVar(newData, 'det');

		// assign instance vars from dataMap
		data = processDataMap(getRequiredVar(newData, 'data'));

		// and then we rebind data.values to the lines
	    //graph.selectAll("g .lines path").data(data.values)
		redrawImage(true)

		// redraw (with transition)
		redrawAxes(true);

		redrawLegend();
		
		handleDataUpdate();
		
		// fire an event that data was updated
		$(container).trigger('LineGraph:dataModification')
	}

	this.switchToPowerScale = function() {
		zScale = 'pow';
		redrawAxes(true);
		redrawImage(true);
		
		// fire an event that config was changed
		$(container).trigger('ImagePlot:configModification')
	}

	this.switchToLogScale = function() {
		zScale = 'log';
		redrawAxes(true);
		redrawImage(true);
		
		// fire an event that config was changed
		$(container).trigger('ImagePlot:configModification')
	}

	this.switchToLinearScale = function() {
		zScale = 'linear';
		redrawAxes(true);		
		redrawImage(true);
		
		// fire an event that config was changed
		$(container).trigger('ImagePlot:configModification')
	}
	
	/**
	 * Return the current scale value: pow, log or linear
	 */
	this.getScale = function() {
		return zScale;
	}

	/* *************************************************************** */
	/* private variables */
	/* *************************************************************** */
	// the div we insert the graph into
	var containerId;
	var container;
	
	// functions we use to display and interact with the graphs and lines
	var context, image, graph, x, y, color, xAxis, yAxis, linesGroup, linesGroupText, lines, lineFunction, w_scale, h_scale;
	var zScale = 'linear'; // can be pow, log, linear
	var scales = [['linear','Linear'], ['pow','Power'], ['log','Log']];
	var hoverContainer, hoverLine1, hoverLine1XOffset, hoverLine1YOffset, hoverLine2, hoverLine2XOffset, hoverLine2YOffset, hoverLineGroup;
	var legendFontSize = 12; // we can resize dynamically to make fit so we remember it here
	// instance storage of data to be displayed
	var data;
	var det;

	// define dimensions of graph
	var margin = [-1, -1, -1, -1]; // margins (top, right, bottom, left)
	var w, h;	 // width & height
	
	var transitionDuration = 300;
	
	var tickFormatForLogScale = ",.01f";
	
	// used to track if the user is interacting via mouse/finger instead of trying to determine
	// by analyzing various element class names to see if they are visible or not
	var userCurrentlyInteracting = false;
	var currentUserPositionX = -1;
	var currentUserPositionY = -1;

	var colorMaps = {
			'reds': ["#e34a33", "#fdbb84", "#fee8c8"],
			'greens' : ["#2ca25f", "#99d8c9", "#e5f5f9"],
			'blues' : ["#2b8cbe", "#a6bddb", "#ece7f2"],
			'purples' : ["#dd1c77", "#c994c7", "#e7e1ef"],
			'oranges' : ["#d95f0e", "#fec44f", "#fff7bc"]
		}
	/* *************************************************************** */
	/* initialization and validation */
	/* *************************************************************** */
	var _init = function() {
		// required variables that we'll throw an error on if we don't find
		containerId = getRequiredVar(argsMap, 'containerId');
		container = document.querySelector('#' + containerId);
		
		// margins with defaults (do this before processDataMap since it can modify the margins)
		margin[0] = getOptionalVar(argsMap, 'marginTop', 20) // marginTop allows fitting the actions, date and top of axis labels
		margin[1] = getOptionalVar(argsMap, 'marginRight', 20)
		margin[2] = getOptionalVar(argsMap, 'marginBottom', 35) // marginBottom allows fitting the legend along the bottom
		margin[3] = getOptionalVar(argsMap, 'marginLeft', 35) // marginLeft allows fitting the axis labels
		
		// Get detector to plot
		det = getRequiredVar(argsMap, 'det')

		// assign instance vars from dataMap
		data = processDataMap(getRequiredVar(argsMap, 'data'));
		
		/* set the default scale */
		zScale = data.scale;

		// do this after processing margins and executing processDataMap above
		initDimensions();

		w_scale = d3.scale.linear().domain([0, w]).range([0, data.h_axis.length])
		h_scale = d3.scale.linear().domain([0, h]).range([0, data.v_axis.length])

		
		createGraph()
		//debug("Initialization successful for container: " + containerId)	
	}
	/* *************************************************************** */
	/* private methods */
	/* *************************************************************** */

	/*
	* Return the value from argsMap for key or throw error if no value found
	*/	  
	var getRequiredVar = function(argsMap, key, message) {
		if(!argsMap[key]) {
			if(!message) {
				throw new Error(key + " is required")
			} else {
				throw new Error(message)
			}
		} else {
			return argsMap[key]
		}
	}

	/**
	* Return the value from argsMap for key or defaultValue if no value found
	*/
	var getOptionalVar = function(argsMap, key, defaultValue) {
		if(!argsMap[key]) {
			return defaultValue
		} else {
			return argsMap[key]
		}
	}

	/**
	* Set height/width dimensions based on container.
	*/
	var initDimensions = function() {
		// automatically size to the container using JQuery to get width/height
		//w = data.v_axis.length;
		//h = data.h_axis.length;
		w = $("#" + containerId).width() - margin[1] - margin[3]; // width
		h=w;
		//h = $("#" + containerId).height() - margin[0] - margin[2]; // height
		
		// make sure to use offset() and not position() as we want it relative to the document, not its parent
		hoverLine1XOffset = margin[3]+$(container).offset().left;
		hoverLine1YOffset = margin[0]+$(container).offset().top;
		hoverLine2XOffset = margin[3]+$(container).offset().left;
		hoverLine2YOffset = margin[0]+$(container).offset().top;
	}

	var processDataMap = function(dataMap) {

		// assign data values to plot over time
		var h_axis = getRequiredVar(dataMap, 'x', "The data object must contain a 'x' value with a data array.");
		var v_axis = getRequiredVar(dataMap, 'y', "The data object must contain a 'y' value with a data array.");
		//var det = getRequiredVar(dataMap, 'det', "The data object must specify a detector.");
		var displayColor = getOptionalVar(dataMap, 'display_color', "blues");
		var true_aspect = getOptionalVar(dataMap, 'true_aspect_ratio', false)

		//h = h_axis.length;
		//w = v_axis.length;


		// Loop over all 
		var dataValues = [];
		var displayNames = [det];
		
		$.each(dataMap, function(key,val){
			if (!isNaN(parseInt(key))) {
				val.forEach(function(v,i){
					if (v.name==det){
						dataValues.push(v.values);
					}
				})
			}
		})


		var numAxisLabelsPowerScale = getOptionalVar(dataMap, 'numAxisLabelsPowerScale', 6); 
		var numAxisLabelsLinearScale = getOptionalVar(dataMap, 'numAxisLabelsLinearScale', 6); 
		
		var maxValuesY = [];
		var minValuesY = [];
		var maxValuesX = [];
		var minValuesX = [];
		var maxValuesZ = [];
		var minValuesZ = [];
		var rounding = getOptionalVar(dataMap, 'rounding', []);
		// default rounding values
		if(rounding.length == 0) {
			displayNames.forEach(function (v, i) {
				// set the default to 0 decimals
				rounding[i] = 1;
			})
		}
		minValuesX[0] = d3.min(h_axis.values)
		maxValuesX[0] = d3.max(h_axis.values)
		minValuesY[0] = d3.min(v_axis.values)
		maxValuesY[0] = d3.max(v_axis.values)
		dataValues.forEach(function (v, i) {
			minValuesZ[i] = d3.min(v)
			maxValuesZ[i] = d3.max(v)
		})
		minValuesZ = [d3.min(minValuesZ)]
		maxValuesZ = [d3.max(maxValuesZ)]
		
		return {
			"h_axis": h_axis.values,
			"x_axis_label": h_axis.name,
			"v_axis": v_axis.values,
			"y_axis_label": v_axis.name,
			"values" : dataValues,
			"displayNames": displayNames,
			"displayColor": displayColor,
			"trueAspect": true_aspect,
			"scale" : getOptionalVar(dataMap, 'scale', zScale),
			"rounding" : rounding,
			"numAxisLabelsLinearScale": numAxisLabelsLinearScale,
			"numAxisLabelsPowerScale": numAxisLabelsPowerScale
		}
	}

	/**
	* Creates the SVG elements and displays the line graph.
	*
	* Expects to be called once during instance initialization.
	*/
	var createGraph = function() {
		// The z-axis is color so update the colormap when the data changes
		initZ();
		
	    image = d3.select("#" + containerId).append("canvas")
				.attr("class", "image-map")
				.attr("width", 	w + margin[1]+margin[2]+'px')
	      		.attr("height", h + margin[0]+margin[3]+'px')
				.style("width", w + margin[1]+margin[2]+'px' )
      			.style("height", h + margin[0]+margin[3]+'px' )
				.call(drawImage);
		
		
		// Add an SVG element with the desired dimensions and margin.
		graph = d3.select("#" + containerId).append("svg:svg")
				.attr("class", "image-graph")
				.attr("width",  w + margin[1]+margin[2] )
				.attr("height", h + margin[0]+margin[3] )	
				.append("svg:g")
				.attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");

		initX()		
		
		// Add the x-axis.
		graph.append("svg:g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + h + ")")
			.call(xAxis);
			
		
		// y is all done in initY because we need to re-assign vars quite often to change scales
		initY();
				
		// Add the y-axis to the left
		graph.append("svg:g")
			.attr("class", "y axis left")
			.attr("transform", "translate(0,0)")
			.call(yAxis);

		// append a group to contain all lines
		lines = graph.append("svg:g")
				.attr("class", "lines");

		// persist this reference so we don't do the selector every mouse event
		hoverContainer = container.querySelector('g .lines');
		
		
		$(container).mouseleave(function(event) {
			handleMouseOutGraph(event);
		})
		
		$(container).mousemove(function(event) {
			handleMouseOverGraph(event);
		})		

			
		// add a 'hover' line that we'll show as a user moves their mouse (or finger)
		// so we can use it to show detailed values of each line
		hoverLineGroup = graph.append("svg:g")
							.attr("class", "hover-line");
		// add the line to the group
		hoverLine1 = hoverLineGroup
			.append("svg:line")
				.attr("x1", 10).attr("x2", 10) // vertical line so same value on each
				.attr("y1", 0).attr("y2", h); // top to bottom
				// add the line to the group
		hoverLine2 = hoverLineGroup
			.append("svg:line")
				.attr("x1", 0).attr("x2", w) // horizontal line so same value on each
				.attr("y1", 10).attr("y2", 10); // right to left	
				
		// hide it by default
		hoverLine1.classed("hide", true);
		hoverLine2.classed("hide", true);
		
		createScaleButtons();
		createDateLabel();
		createLegend();		
		setValueLabelsToLatest();
	}

	/**
	 * Create scale buttons for switching the y-axis
	 */
	var createScaleButtons = function() {
		var cumulativeWidth = 0;		
		// append a group to contain all lines
		var buttonGroup = graph.append("svg:g")
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
					if(d[0] == zScale) {
						return "black";
					} else {
						return "blue";
					}
				})
				.classed("selected", function(d) {
					if(d[0] == zScale) {
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
			self.switchToLinearScale();
		} else if(index == 1) {
			self.switchToPowerScale();
		} else if(index == 2) {
			self.switchToLogScale();
		}
		
		// change text decoration
		graph.selectAll('.scale-button')
		.attr("fill", function(d) {
			if(d[0] == zScale) {
				return "black";
			} else {
				return "blue";
			}
		})
		.classed("selected", function(d) {
			if(d[0] == zScale) {
				return true;
			} else {
				return false;
			}
		})
		
	}


	/*
	 * Whenever we add/update data we want to re-calculate if the max Y scale has changed
	 */
	var calculateExtremaZ = function(data) {
		minValuesZ = [];
		maxValuesZ = [];
		data.values.forEach(function(v, i){
			maxValuesZ.push(d3.max(v));
			minValuesZ.push(d3.min(v));
		})

		var absmin = d3.min(minValuesZ);
		var absmax = d3.max(maxValuesZ);
		if (absmin==absmax){
			absmin-=1;
			absmax+=1;
		}
		minValuesZ = [absmin];
		maxValuesZ = [absmax];

		return [absmin, 0.5*(absmax+absmin) ,absmax];
	}

	/*
	* Allow re-initializing the x function at any time.
	*/
	var initX = function() {
		x = d3.scale.linear().domain([data.h_axis[0], data.h_axis[data.h_axis.length-1]]).range([0, w]);
		
		// create xAxis (with ticks)
		xAxis = d3.svg.axis().scale(x).orient("bottom");
	}

	/*
	* Allow re-initializing the x function at any time.
	*/
	var initY = function() {
		y = d3.scale.linear().domain([data.v_axis[0], data.v_axis[data.v_axis.length-1]]).range([h, 0]);
		// create xAxis (with ticks)
		yAxis = d3.svg.axis().scale(y).orient("left");
	}

	var initZ = function(){

		extremaZ = calculateExtremaZ(data)
		if(zScale == 'pow') {
			color = d3.scale.pow().exponent(0.3).domain(extremaZ).range(colorMaps[data.displayColor]).nice();	
		} else if(zScale == 'log') {
			// we can't have 0 so will represent 0 with a very small number
			// 0.1 works to represent 0, 0.01 breaks the tickFormatter
			color = d3.scale.log().domain([0.1, 0.5*extremaZ[2], extremaZ[2]]).range(colorMaps[data.displayColor]).nice();	
		} else if(zScale == 'linear') {
			color = d3.scale.linear().domain(extremaZ).range(colorMaps[data.displayColor]).nice();
		}
		color.clamp(true)
	}
	
	// Compute the pixel colors; scaled by CSS.
  	function drawImage(canvas) {
	    var context = canvas.node().getContext("2d"),
	    //image = context.createImageData(data.h_axis.length, data.v_axis.length);
	    image = context.createImageData(w, h);
	    for (var y = h-1, p = -1; y >= 0; --y) {
	    	for (var x = 0; x < w; ++x) {
	      
		      	if (Math.floor(h_scale(y))<data.values.length){
					var c = d3.rgb(color(data.values[Math.floor(h_scale(y))][Math.floor(w_scale(x))]));
			        image.data[++p] = c.r;
			        image.data[++p] = c.g;
			        image.data[++p] = c.b;
			        image.data[++p] = 255;
		      	}
		      	else { 
		      		y=-1;
		      		break;
		      	}
	      }
	    }

	    context.putImageData(image, margin[3], margin[0]);
  	}

	/**
	 * Called when a user mouses over the graph.
	 */
	var handleMouseOverGraph = function(event) {	
		var mouseX = event.pageX-hoverLine1XOffset;
		var mouseY = event.pageY-hoverLine1YOffset;
		
		//debug("MouseOver graph [" + containerId + "] => x: " + mouseX + " y: " + mouseY + "  height: " + h + " event.clientY: " + event.clientY + " offsetY: " + event.offsetY + " pageY: " + event.pageY + " hoverLineYOffset: " + hoverLineYOffset)
		if(mouseX >= 0 && mouseX <= w && mouseY >= 0 && mouseY <= h) {
			// show the hover line
			hoverLine1.classed("hide", false);
			hoverLine2.classed("hide", false);

			// set position of hoverLine
			hoverLine1.attr("x1", mouseX).attr("x2", mouseX)
			hoverLine2.attr("y1", mouseY).attr("y2", mouseY)
			
			displayValueLabelsForPositionXY(mouseX, mouseY)
			
			// user is interacting
			userCurrentlyInteracting = true;
			currentUserPositionX = mouseX;
			currentUserPositionY = mouseY;
		} else {
			// proactively act as if we've left the area since we're out of the bounds we want
			handleMouseOutGraph(event)
		}
	}

	var handleMouseOutGraph = function(event) {	
		// hide the hover-line
		hoverLine1.classed("hide", true);
		hoverLine2.classed("hide", true);
		
		setValueLabelsToLatest();
		
		// user is no longer interacting
		userCurrentlyInteracting = false;
		currentUserPositionX = -1;
		currentUserPositionY = -1;
	}

	/**
	* Display the data values at position X in the legend value labels.
	*/
	var displayValueLabelsForPositionXY = function(xPosition, yPosition, withTransition) {
		var animate = false;
		if(withTransition != undefined) {
			if(withTransition) {
				animate = true;
			}
		}
		var xyToShow;
		var labelValueWidths = [];
		graph.selectAll("text.legend.value")
		.text(function(d, i) {
			var valuesForX = getValueForPositionXFromData(xPosition, yPosition);
			xyToShow = valuesForX;
			//debug('xPosition: ' +xPosition+ 'value: '+valuesForX.value)
			return valuesForX.value;
		})
		.attr("x", function(d, i) {
			labelValueWidths[i] = this.getComputedTextLength();
		})

		// position label names
		var cumulativeWidth = 0;
		var labelNameEnd = [];
		graph.selectAll("text.legend.name")
			.attr("x", function(d, i) {
				// return it at the width of previous labels (where the last one ends)
				var returnX = cumulativeWidth;
				// increment cumulative to include this one + the value label at this index
				cumulativeWidth += this.getComputedTextLength()+4+labelValueWidths[i]+8;
				// store where this ends
				labelNameEnd[i] = returnX + this.getComputedTextLength()+5;
				return returnX;
			})

		// remove last bit of padding from cumulativeWidth
		cumulativeWidth = cumulativeWidth - 8;

		if(cumulativeWidth > w) {
			// decrease font-size to make fit
			legendFontSize = legendFontSize-1;
			//debug("making legend fit by decreasing font size to: " + legendFontSize)
			graph.selectAll("text.legend.name")
				.attr("font-size", legendFontSize);
			graph.selectAll("text.legend.value")
				.attr("font-size", legendFontSize);
			
			// recursively call until we get ourselves fitting
			displayValueLabelsForPositionXY(xPosition, yPosition);
			return;
		}

		// position label values
		graph.selectAll("text.legend.value")
		.attr("x", function(d, i) {
			return labelNameEnd[i];
		})
		

		// show the date
		graph.select('text.date-label').text('x: '+xyToShow.x_val+', y: '+xyToShow.y_val)

		// move the group of labels to the right side
		if(animate) {
			graph.selectAll("g.legend-group g")
				.transition()
				.duration(transitionDuration)
				.ease("linear")
				.attr("transform", "translate(" + (w-cumulativeWidth) +",0)")
		} else {
			graph.selectAll("g.legend-group g")
				.attr("transform", "translate(" + (w-cumulativeWidth) +",0)")
		}
	}

	var getValueForPositionXFromData = function(xPosition, yPosition) {
		
		// get the date on x-axis for the current location
		var xValue = x.invert(xPosition);
		var yValue = y.invert(yPosition);

		// Calculate the value from this date by determining the 'index'
		// within the data array that applies to this value
		var indexX = 0;
		
		for (var i = 0; i < data.h_axis.length; i++) {
			if (data.h_axis[i]<xValue){
				indexX = i;
			}
		};

		if (indexX >= data.h_axis.length) {
			indexX = data.h_axis.length-1;
		}

		var indexY = 0;
		for (var i = 0; i < data.v_axis.length; i++) {
			if (data.v_axis[i]<yValue){
				indexY = i;
			}
		};


		if(indexY >= data.v_axis.length) {
			indexY = data.v_axis.length-1;
		}
		
		// The date we're given is interpolated so we have to round off to get the nearest
		// index in the data array for the xValue we're given.
		// Once we have the index, we then retrieve the data from the d[] array
		indexX = Math.round(indexX);
		indexY = Math.round(indexY);
		try {
			// This index may not have been measured yet
			var v = data.values[indexY][indexX];
		}
		catch (err){
			console.log('v err')
			var v = 0.0;
		}

		var roundToNumDecimals = data.rounding[0];

		return {value: roundNumber(v, roundToNumDecimals), x_val: roundNumber(xValue, 3), y_val: roundNumber(yValue, 3)};
	}

	/* round a number to X digits: num => the number to round, dec => the number of decimals */
	function roundNumber(num, dec) {
		var result = Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
		var resultAsString = result.toString();
		if(dec > 0) {
			if(resultAsString.indexOf('.') == -1) {
				resultAsString = resultAsString + '.';
			}
			// make sure we have a decimal and pad with 0s to match the number we were asked for
			var indexOfDecimal = resultAsString.indexOf('.');
			while(resultAsString.length <= (indexOfDecimal+dec)) {
				resultAsString = resultAsString + '0';
			}
		}
		return resultAsString;
	};

	var redrawAxes = function(withTransition) {
		lg = $('#'+containerId)[0].getElementsByClassName('image-graph');
		lg[0].parentElement.removeChild(lg[0]);
		initX();
		initY();
		initZ();
		
	}

	var redrawImage = function(withTransition) {

		lg = $('#'+containerId)[0].getElementsByClassName('image-map');
		lg[0].parentElement.removeChild(lg[0]);
		createGraph()

	}

	/**
	 * Create a data label
	 */
	var createDateLabel = function() {
		// create the date label to the left of the scaleButtons group
		var buttonGroup = graph.append("svg:g")
				.attr("class", "date-label-group")
			.append("svg:text")
				.attr("class", "date-label")
				.attr("text-anchor", "end") // set at end so we can position at far right edge and add text from right to left
				.attr("font-size", "10") 
				.attr("y", -4)
				.attr("x", w)
				.text("NA")		
	}
	
	var setValueLabelsToLatest = function(withTransition) {
		displayValueLabelsForPositionXY(w, h, withTransition);
	}

	/**
	 * Create a legend that displays the name of each line with appropriate color coding
	 * and allows for showing the current value when doing a mouseOver
	 */
	var createLegend = function() {
		
		// append a group to contain all lines
		var legendLabelGroup = graph.append("svg:g")
				.attr("class", "legend-group")
			.selectAll("g")
				.data(data.displayNames)
			.enter().append("g")
				.attr("class", "legend-labels");
				
		legendLabelGroup.append("svg:text")
				.attr("class", "legend name")
				.text(function(d, i) {
					return d;
				})
				.attr("font-size", legendFontSize)
				.attr("fill", function(d, i) {
					// return the color for this row
					return color[maxValuesZ[0]];
				})
				.attr("y", function(d, i) {
					return h+28;
				})

		// put in placeholders with 0 width that we'll populate and resize dynamically
		legendLabelGroup.append("svg:text")
				.attr("class", "legend value")
				.attr("font-size", legendFontSize)
				.attr("fill", function(d, i) {
					return color[maxValuesZ[0]];
				})
				.attr("y", function(d, i) {
					return h+28;
				})
				
		// x values are not defined here since those get dynamically calculated when data is set in displayValueLabelsForPositionX()
	}

	var redrawLegend = function(){
		lg = $('#'+containerId)[0].getElementsByClassName('legend-group');
		lg[0].parentElement.removeChild(lg[0]);
		createLegend();
	}

	/*
	* Handler for when data is updated.
	*/
	var handleDataUpdate = function() {
		if(userCurrentlyInteracting) {
			// user is interacting, so let's update values to wherever the mouse/finger is on the updated data
			if(currentUserPositionX > -1) {
				displayValueLabelsForPositionX(currentUserPositionX)
			}
		} else {
			// the user is not interacting with the graph, so we'll update the labels to the latest
			setValueLabelsToLatest();
		}
	}

	var error = function(message) {
		console.log("ERROR: " + message)
	}

	var debug = function(message) {
		console.log("DEBUG: " + message)
	}

	_init()
}