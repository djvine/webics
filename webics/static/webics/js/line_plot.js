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


function LinePlot(argsMap){

	/* *************************************************************** */
	/* public methods */
	/* *************************************************************** */
	var self = this;

	/**
	 * This does a full refresh of the data:
	 * - x-axis will slide to new range
	 * - lines will change in place
	 * row - the row number to display
	 * dets - an array of detector names to display e.g. ['D01', 'D07']
	 */
	this.updateData = function(newData, row, dets) {
		// data is being replaced, not appended so we re-assign 'data'
		data = processDataMap(newData, row, dets);
		// and then we rebind data.values to the lines
	    //graph.selectAll("g .lines path").data(data.values)
		rebindData(data)
		// redraw (with transition)
		redrawAxes(true);
		// transition is 'false' for lines because the transition is really weird when the data significantly changes
		// such as going from 700 points to 150 to 400
		// and because of that we rebind the data anyways which doesn't work with transitions very well at all
		redrawLines(false);

		redrawLegend();
		
		handleDataUpdate();
		
		// fire an event that data was updated
		$(container).trigger('LineGraph:dataModification')
	}

	
	this.switchToPowerScale = function() {
		yScale = 'pow';
		redrawAxes(true);
		redrawLines(true);
		
		// fire an event that config was changed
		$(container).trigger('LineGraph:configModification')
	}

	this.switchToLogScale = function() {
		yScale = 'log';
		redrawAxes(true);
		redrawLines(true);
		
		// fire an event that config was changed
		$(container).trigger('LineGraph:configModification')
	}

	this.switchToLinearScale = function() {
		yScale = 'linear';
		redrawAxes(true);		
		redrawLines(true);
		
		// fire an event that config was changed
		$(container).trigger('LineGraph:configModification')
	}
	
	/**
	 * Return the current scale value: pow, log or linear
	 */
	this.getScale = function() {
		return yScale;
	}

	/* *************************************************************** */
	/* private variables */
	/* *************************************************************** */
	// the div we insert the graph into
	var containerId;
	var container;
	
	// functions we use to display and interact with the graphs and lines
	var graph, x, y, xAxis, yAxis, linesGroup, linesGroupText, lines, lineFunction;
	var yScale = 'linear'; // can be pow, log, linear
	var scales = [['linear','Linear'], ['pow','Power'], ['log','Log']];
	var hoverContainer, hoverLine, hoverLineXOffset, hoverLineYOffset, hoverLineGroup;
	var legendFontSize = 12; // we can resize dynamically to make fit so we remember it here
	var dets = ['D01']
	// instance storage of data to be displayed
	var data;
		
	// define dimensions of graph
	var margin = [-1, -1, -1, -1]; // margins (top, right, bottom, left)
	var w, h;	 // width & height
	
	var transitionDuration = 300;
	
	var tickFormatForLogScale = ",.01f";
	
	// used to track if the user is interacting via mouse/finger instead of trying to determine
	// by analyzing various element class names to see if they are visible or not
	var userCurrentlyInteracting = false;
	var currentUserPositionX = -1;

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
		margin[3] = getOptionalVar(argsMap, 'marginLeft', 90) // marginLeft allows fitting the axis labels
		
		// assign instance vars from dataMap
		data = processDataMap(getRequiredVar(argsMap, 'data'), 0, dets);
		
		/* set the default scale */
		yScale = data.scale;

		// do this after processing margins and executing processDataMap above
		initDimensions();
		
		createGraph()
		//debug("Initialization successful for container: " + containerId)	
	}
	/* *************************************************************** */
	/* private methods */
	/* *************************************************************** */
	/*
	 * Return a validated data map
	 * 
	 * Expects a map like this:
	 *   {
	 		"x": {"name": "X Axis Label", "values": [1,2,3]}, 
	 		"0": [{"name":"D01", "values":[4,5,6]}, {"name":"D02", "values":[7,8,9]}], 
	 		"1": [{"name":"D01", "values":[10,11,12]}, {"name":"D02", "values":[13,14,15]}]
	 	}
	 */
	var processDataMap = function(dataMap, row, dets) {
		// assign data values to plot over time
		var positioner_axis = getRequiredVar(dataMap, 'x', "The data object must contain a 'x' value with a data array.");
		// Loop over all 
		var dataValues = []
		var displayNames = [];
		if (!dets){
			dataMap[row].forEach(function(v,i){
			dataValues.push(v.values);
			displayNames[i] = v.name;
			})
		} else {
			for (var i = 0; i < dets.length; i++) {
				dataMap[row].forEach(function(v){
					if (v.name==dets[i]){
						dataValues.push(v.values);
						displayNames[i] = v.name;
					}
				})
			};
		}		

		var numAxisLabelsPowerScale = getOptionalVar(dataMap, 'numAxisLabelsPowerScale', 6); 
		var numAxisLabelsLinearScale = getOptionalVar(dataMap, 'numAxisLabelsLinearScale', 6); 

		var colors = ["tomato", "royalblue", "aqua", "greenyellow", "aquamarine", "black", "blue", "blueviolet",
		  "brown", "cadetblue", "chatreuse", "chocolate", "coral",
		  "cornflowerblue", "crimson", "cyan", "darkblue", "darkcyan",
		  "darkgoldenrod", "darkgray", "darkgreen", "darkmagenta", "darkolivegreen",
		  "darkorange", "darkorchid", "darkred", "darkslateblue", "darkslategray",
		  "firebrick", "forestgreen", "fuchsia", "gold", "green",
		  "hotpink", "goldenrod", "gray",  "indianred",
		  "indigo", "lawngreen", "lightblue", "lightcoral", "lightgreen",
		  "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray",
		  "lime", "magenta", "maroon", "mediumblue", "mediumorchid",
		  "navy", "olive", "olivedrab", "orange", "orangered",
		  "orchid", "palegreen", "palevioletred", "peru", "purple",
		  "red",  "saddlebrown", "seagreen", "slateblue",
		  "slategray", "yellow", "teal", "violet"]
		
		var maxValues = [];
		var minValues = [];
		var maxValuesX = [];
		var minValuesX = [];
		var rounding = getOptionalVar(dataMap, 'rounding', []);
		// default rounding values
		if(rounding.length == 0) {
			displayNames.forEach(function (v, i) {
				// set the default to 0 decimals
				rounding[i] = 1;
			})
		}
		dataValues.forEach(function (v, i) {
			minValues[i] = d3.min(v)
			maxValues[i] = d3.max(v)
		})
		
		return {
			"positioner_axis": positioner_axis.values,
			"x_axis_label": positioner_axis.name,
			"values" : dataValues,
			"displayNames": displayNames,
			"colors": colors,
			"scale" : getOptionalVar(dataMap, 'scale', yScale),
			"maxValues" : maxValues,
			"rounding" : rounding,
			"numAxisLabelsLinearScale": numAxisLabelsLinearScale,
			"numAxisLabelsPowerScale": numAxisLabelsPowerScale
		}
	}

	var redrawLegend = function(){
		lg = document.getElementsByClassName('legend-group');
		lg[0].parentElement.removeChild(lg[0]);
		createLegend();
	}

	var redrawAxes = function(withTransition) {
		initY();
		initX();
		
		if(withTransition) {
			// slide x-axis to updated location
			graph.selectAll("g .x.axis").transition()
			.duration(transitionDuration)
			.ease("linear")
			.call(xAxis)				  
		
			// slide y-axis to updated location
			graph.selectAll("g .y.axis.left").transition()
			.duration(transitionDuration)
			.ease("linear")
			.call(yAxis)
			
		} else {
			// slide x-axis to updated location
			graph.selectAll("g .x.axis")
			.call(xAxis)				  
		
			// slide y-axis to updated location
			graph.selectAll("g .y.axis.left")
			.call(yAxis)
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
		lineFunctionSeriesIndex  =-1;
		
		// redraw lines
		if(withTransition) {
			graph.selectAll("g .lines path")
			.transition()
				.duration(transitionDuration)
				.ease("linear")
				.attr("d", lineFunction)
				.attr("transform", null);
		} else {
			graph.selectAll("g .lines path")
				.attr("d", lineFunction)
				.attr("transform", null);
		}
	}

	/**
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
		w = $("#" + containerId).width() - margin[1] - margin[3]; // width
		h = $("#" + containerId).height() - margin[0] - margin[2]; // height
		
		// make sure to use offset() and not position() as we want it relative to the document, not its parent
		hoverLineXOffset = margin[3]+$(container).offset().left;
		hoverLineYOffset = margin[0]+$(container).offset().top;
	}

	/*
	 * Whenever we add/update data we want to re-calculate if the max Y scale has changed
	 */
	var calculateExtremaY = function(data) {
		minValues = [];
		maxValues = [];
		data.values.forEach(function(v, i){
			maxValues.push(d3.max(v));
			minValues.push(d3.min(v));
		})

		var absmin = d3.min(minValues);
		var absmax = d3.max(maxValues);
		if (absmin==absmax){
			absmin-=1;
			absmax+=1;
		}

		return [absmin, absmax];
	}

	/*
	 * Whenever we add/update data we want to re-calculate if the max X scale has changed
	 */
	var calculateExtremaX = function(data) {
		minValuesX = [];
		maxValuesX = [];
		
		maxValuesX.push(d3.max(data.positioner_axis));
		minValuesX.push(d3.min(data.positioner_axis));
		return [minValuesX[0], maxValuesX[0]];
	}

	var initY = function() {
		var extremaY = calculateExtremaY(data)
		
		var numAxisLabels = 6;
		if(yScale == 'pow') {
			y = d3.scale.pow().exponent(0.3).domain([0, extremaY[1]]).range([h, 0]).nice();	
			numAxisLabels = data.numAxisLabelsPowerScale;
		} else if(yScale == 'log') {
			// we can't have 0 so will represent 0 with a very small number
			// 0.1 works to represent 0, 0.01 breaks the tickFormatter
			y = d3.scale.log().domain([0.1, extremaY[1]]).range([h, 0]).nice();	
		} else if(yScale == 'linear') {
			y = d3.scale.linear().domain([extremaY[0], extremaY[1]]).range([h, 0]).nice();
			numAxisLabels = data.numAxisLabelsLinearScale;
		}
		y.clamp(true)

		yAxis = d3.svg.axis().scale(y).ticks(numAxisLabels, tickFormatForLogScale).orient("left");
	}

	/*
	 * Allow re-initializing the x function at any time.
	 */
	var initX = function() {
		x = d3.scale.linear().domain(calculateExtremaX(data)).range([0, w]);
		
		// create xAxis (with ticks)
		xAxis = d3.svg.axis().scale(x).tickSize(-h).tickSubdivide(1);
	}

	var rebindData = function(data){
		lg = document.getElementsByClassName('lines');
		lg[0].parentElement.removeChild(lg[0]);

		// create line function used to plot our data
		lineFunction = d3.svg.line()
			// assign the X function to plot our line as we wish
			.x(function(d,i) { 
				//debug("Line X => data: " + data.positioner_axis[i] + " scale: " + x(data.positioner_axis[i]));
				return x(data.positioner_axis[i]);
			})
			.y(function(d, i) { 
				if(yScale == 'log' && d < 0.1) {
					// log scale can't have 0s, so we set it to the smallest value we set on y
					d = 0.1;
				}
				//debug("Line Y => data: " + d + " scale: " + y(d))
				return y(d);
			});
			//if (yScale=='log'){
			//	lineFunction.defined(function(d) {
				// handle missing data gracefully
				// feature added in https://github.com/mbostock/d3/pull/594
			//	return d > 0;
			//	}
			//)};
			

		// append a group to contain all lines
		lines = graph.append("svg:g")
				.attr("class", "lines")
				.selectAll("path")
				.data(data.values); // bind the array of arrays

		// persist this reference so we don't do the selector every mouse event
		hoverContainer = container.querySelector('g .lines');
		
		
		$(container).mouseleave(function(event) {
			handleMouseOutGraph(event);
		})
		
		$(container).mousemove(function(event) {
			handleMouseOverGraph(event);
		})		

		
		// add a line group for each array of values (it will iterate the array of arrays bound to the data function above)
		linesGroup = lines.enter().append("g")
				.attr("class", function(d, i) {
					return "line_group series_" + i;
				});
				
		// add path (the actual line) to line group
		linesGroup.append("path")
				.attr("class", function(d, i) {
					//debug("Appending line [" + containerId + "]: " + i)
					return "line series_" + i;
				})
				.attr("fill", "none")
				.attr("stroke", function(d, i) {
					return d3.rgb(data.colors[i]).toString();
				})
				.attr("d", lineFunction) // use the 'lineFunction' to create the data points in the correct x,y axis
				.on('mouseover', function(d, i) {
					handleMouseOverLine(d, i);
				});
		
		// add line label to line group
		linesGroupText = linesGroup.append("svg:text");
		linesGroupText.attr("class", function(d, i) {
				//debug("Appending line [" + containerId + "]: " + i)
				return "line_label series_" + i;
			})
			.text(function(d, i) {
				return "";
			});
		xlg = document.getElementsByClassName('xaxis-label-group');
		xlg[0].parentElement.removeChild(xlg[0]);
		createXAxisLabel(data.x_axis_label);
	}

	/**
	* Creates the SVG elements and displays the line graph.
	*
	* Expects to be called once during instance initialization.
	*/
	var createGraph = function() {
		
		// Add an SVG element with the desired dimensions and margin.
		graph = d3.select("#" + containerId).append("svg:svg")
				.attr("class", "line-graph")
				.attr("width", w + margin[1] + margin[3])
				.attr("height", h + margin[0] + margin[2])	
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
				
		// create line function used to plot our data
		lineFunction = d3.svg.line()
			// assign the X function to plot our line as we wish
			.x(function(d,i) { 
				//debug("Line X => data: " + data.positioner_axis[i] + " scale: " + x(data.positioner_axis[i]));
				return x(data.positioner_axis[i]);
			})
			.y(function(d, i) { 
				if(yScale == 'log' && d < 0.1) {
					// log scale can't have 0s, so we set it to the smallest value we set on y
					d = 0.1;
				}
				//debug("Line Y => data: " + d + " scale: " + y(d))
				return y(d);
			});
			//if (yScale=='log'){
			//	lineFunction.defined(function(d) {
				// handle missing data gracefully
				// feature added in https://github.com/mbostock/d3/pull/594
			//	return d > 0;
			//	}
			//)};
			

		// append a group to contain all lines
		lines = graph.append("svg:g")
				.attr("class", "lines")
				.selectAll("path")
				.data(data.values); // bind the array of arrays

		// persist this reference so we don't do the selector every mouse event
		hoverContainer = container.querySelector('g .lines');
		
		
		$(container).mouseleave(function(event) {
			handleMouseOutGraph(event);
		})
		
		$(container).mousemove(function(event) {
			handleMouseOverGraph(event);
		})		

		
		// add a line group for each array of values (it will iterate the array of arrays bound to the data function above)
		linesGroup = lines.enter().append("g")
				.attr("class", function(d, i) {
					return "line_group series_" + i;
				});
				
		// add path (the actual line) to line group
		linesGroup.append("path")
				.attr("class", function(d, i) {
					//debug("Appending line [" + containerId + "]: " + i)
					return "line series_" + i;
				})
				.attr("fill", "none")
				.attr("stroke", function(d, i) {
					return d3.rgb(data.colors[i]).toString();
				})
				.attr("d", lineFunction) // use the 'lineFunction' to create the data points in the correct x,y axis
				.on('mouseover', function(d, i) {
					handleMouseOverLine(d, i);
				});
		
		// add line label to line group
		linesGroupText = linesGroup.append("svg:text");
		linesGroupText.attr("class", function(d, i) {
				//debug("Appending line [" + containerId + "]: " + i)
				return "line_label series_" + i;
			})
			.text(function(d, i) {
				return "";
			});
			
		// add a 'hover' line that we'll show as a user moves their mouse (or finger)
		// so we can use it to show detailed values of each line
		hoverLineGroup = graph.append("svg:g")
							.attr("class", "hover-line");
		// add the line to the group
		hoverLine = hoverLineGroup
			.append("svg:line")
				.attr("x1", 10).attr("x2", 10) // vertical line so same value on each
				.attr("y1", 0).attr("y2", h); // top to bottom	
				
		// hide it by default
		hoverLine.classed("hide", true);
		
		createScaleButtons();
		createDateLabel();
		createLegend();		
		setValueLabelsToLatest();
		createXAxisLabel(data.x_axis_label);
	}

	/**
	 * Label the x axis
	 */
	var createXAxisLabel = function(lbl) {

		var aAxisLabel_Group = graph.append("svg:g")
				.attr("class", "xaxis-label-group")
			.append("svg:text")
				.attr("class", "xaxis-label")
				.attr("text-anchor", "start") // set at end so we can position at far right edge and add text from right to left
				.attr("font-size", "10") 
				.attr("y", h+30)
				.attr("x", 150)
				.text(lbl)		
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
					return data.colors[i];
				})
				.attr("y", function(d, i) {
					return h+28;
				})

				
		// put in placeholders with 0 width that we'll populate and resize dynamically
		legendLabelGroup.append("svg:text")
				.attr("class", "legend value")
				.attr("font-size", legendFontSize)
				.attr("fill", function(d, i) {
					return data.colors[i];
				})
				.attr("y", function(d, i) {
					return h+28;
				})
				
		// x values are not defined here since those get dynamically calculated when data is set in displayValueLabelsForPositionX()
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
			self.switchToLinearScale();
		} else if(index == 1) {
			self.switchToPowerScale();
		} else if(index == 2) {
			self.switchToLogScale();
		}
		
		// change text decoration
		graph.selectAll('.scale-button')
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

	/**
	 * Create a data label
	 */
	var createDateLabel = function() {
		var date = new Date(); // placeholder just so we can calculate a valid width
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

	/**
	 * Called when a user mouses over a line.
	 */
	var handleMouseOverLine = function(lineData, index) {
		
		// user is interacting
		userCurrentlyInteracting = true;
	}

	/**
	 * Called when a user mouses over the graph.
	 */
	var handleMouseOverGraph = function(event) {	
		var mouseX = event.pageX-hoverLineXOffset+5;
		var mouseY = event.pageY-hoverLineYOffset;
		
		//debug("MouseOver graph [" + containerId + "] => x: " + mouseX + " y: " + mouseY + "  height: " + h + " event.clientY: " + event.clientY + " offsetY: " + event.offsetY + " pageY: " + event.pageY + " hoverLineYOffset: " + hoverLineYOffset)
		if(mouseX >= 0 && mouseX <= w && mouseY >= 0 && mouseY <= h) {
			// show the hover line
			hoverLine.classed("hide", false);

			// set position of hoverLine
			hoverLine.attr("x1", mouseX).attr("x2", mouseX)
			
			displayValueLabelsForPositionX(mouseX)
			
			// user is interacting
			userCurrentlyInteracting = true;
			currentUserPositionX = mouseX;
		} else {
			// proactively act as if we've left the area since we're out of the bounds we want
			handleMouseOutGraph(event)
		}
	}

	var handleMouseOutGraph = function(event) {	
		// hide the hover-line
		hoverLine.classed("hide", true);
		
		setValueLabelsToLatest();
		
		// user is no longer interacting
		userCurrentlyInteracting = false;
		currentUserPositionX = -1;
	}

	/**
	* Display the data values at position X in the legend value labels.
	*/
	var displayValueLabelsForPositionX = function(xPosition, withTransition) {
		var animate = false;
		if(withTransition != undefined) {
			if(withTransition) {
				animate = true;
			}
		}
		var xToShow;
		var labelValueWidths = [];
		graph.selectAll("text.legend.value")
		.text(function(d, i) {
			var valuesForX = getValueForPositionXFromData(xPosition, i);
			xToShow = valuesForX;
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
			displayValueLabelsForPositionX(xPosition);
			return;
		}

		// position label values
		graph.selectAll("text.legend.value")
		.attr("x", function(d, i) {
			return labelNameEnd[i];
		})
		

		// show the date
		graph.select('text.date-label').text(xToShow.x_val)

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

	var getValueForPositionXFromData = function(xPosition, dataSeriesIndex) {
		var d = data.values[dataSeriesIndex]
		
		// get the date on x-axis for the current location
		var xValue = x.invert(xPosition);

		// Calculate the value from this date by determining the 'index'
		// within the data array that applies to this value
		var index = 0;
		for (var i = 0; i < d.length; i++) {
			if (data.positioner_axis[i]<xValue){
				index = i;
			}
		};


		if(index >= d.length) {
			index = d.length-1;
		}
		// The date we're given is interpolated so we have to round off to get the nearest
		// index in the data array for the xValue we're given.
		// Once we have the index, we then retrieve the data from the d[] array
		index = Math.round(index);
		var v = d[index];		

		var roundToNumDecimals = data.rounding[dataSeriesIndex];

		return {value: roundNumber(v, roundToNumDecimals), x_val: roundNumber(xValue, 3)};
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

	/**
	* Set the value labels to whatever the latest data point is.
	*/
	var setValueLabelsToLatest = function(withTransition) {
		displayValueLabelsForPositionX(w, withTransition);
	}

	var error = function(message) {
		console.log("ERROR: " + message)
	}

	var debug = function(message) {
		console.log("DEBUG: " + message)
	}

	_init()
}