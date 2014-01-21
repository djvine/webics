function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

function toggle_state(button_id)
{
	if (hasClass(document.getElementById(button_id), 'btn-primary')){
		document.getElementById(button_id).className = "btn btn-success btn-xs";
	}
	else {
		document.getElementById(button_id).className = "btn btn-primary btn-xs";
	}
}

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

dataset = dataset.map( function (d) { 
    return { 
      name: d['name'],   // the + sign will coerce strings to number values
      x: d['x'],
      y: d['y'] 
  	}; 
});   

dataset = d3.nest().key(function(d) { return d.name; }).entries(dataset	);

var h=300;
var w=500;

var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = w - margin.left - margin.right,
    height = h - margin.top - margin.bottom;

var xScale = d3.scale.linear()
                     .range([margin.left, w-margin.right]);
xScale.domain([d3.min(dataset, function(d) { return d3.min(d.values, function (d) { return d.x; }); }), 
	           d3.max(dataset, function(d) { return d3.max(d.values, function (d) { return d.x; }); })]).nice();

var yScale = d3.scale.linear()
                     .range([margin.bottom, h-margin.top]);
yScale.domain([d3.max(dataset, function(d) { return d3.max(d.values, function (d) { return d.y; }); }), 
	           d3.min(dataset, function(d) { return d3.min(d.values, function (d) { return d.y; }); })]).nice();

var color = d3.scale.category10()
    .domain(d3.keys(dataset[0]).filter(function(key) { return key === "name"; }));

var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom")
    .ticks(5);

var yAxis = d3.svg.axis()
    .scale(yScale)
    .orient("left")
    .ticks(5);

var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) { return xScale(d.x); })
    .y(function(d) { console.log(d); return yScale(d.y); });

var svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
    .attr("class", "axis")  //Assign "axis" class
    .attr("transform", "translate(0," + (h - margin.bottom-10) + ")")
    .call(xAxis);

svg.append("g")
    .attr("class", "axis")  //Assign "axis" class
    .attr("transform", "translate(" + margin.left + ",0)")
    .call(yAxis);

var scans = svg.selectAll(".scan")
      .data(dataset, function(d) { return d.key; })
      .enter().append("g")
      .attr("class", "scan");

  scans.append("path")
      .attr("class", "line")
      .attr("d", function(d) { return line(d.values); })
      .style("stroke", function(d) { return color(d.key); });