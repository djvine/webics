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

	/* *************************************************************** */
	/* private variables */
	/* *************************************************************** */

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

	var processDataMap = function(dataMap, det, displayColor) {
		// assign data values to plot over time
		var h_axis = getRequiredVar(dataMap, 'x', "The data object must contain a 'x' value with a data array.");
		var v_axis = getRequiredVar(dataMap, 'y', "The data object must contain a 'y' value with a data array.");
		// Loop over all 
		var dataValues = []
		var displayName = getOptionalVar(dataMap, 'name', det);

		var numAxisLabelsPowerScale = getOptionalVar(dataMap, 'numAxisLabelsPowerScale', 6); 
		var numAxisLabelsLinearScale = getOptionalVar(dataMap, 'numAxisLabelsLinearScale', 6); 

		colorMaps = {
			'reds': ["#fee8c8", "#fdbb84", "#e34a33"],
			'greens' : ["#e5f5f9", "#99d8c9", "#2ca25f"],
			'blues' : ["#ece7f2", "#a6bddb", "#2b8cbe"],
			'purples' : ["#e7e1ef", "#c994c7", "#dd1c77"],
			'oranges' : ["#fff7bc", "#fec44f", "#d95f0e"]
		}

		

		var color = d3.scale.linear()
      		.domain([0, 127, 255])
      		.range(colorMaps[displayColor]);
		
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


		var error = function(message) {
		console.log("ERROR: " + message)
	}

	var debug = function(message) {
		console.log("DEBUG: " + message)
	}

	_init()
}