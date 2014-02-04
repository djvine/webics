var width = 960,
    height = 500;

margin = 10;

reds = ["#fee8c8", "#fdbb84", "#e34a33"]
greens = ["#e5f5f9", "#99d8c9", "#2ca25f"]
blues = ["#ece7f2", "#a6bddb", "#2b8cbe"]
purples = ["#e7e1ef", "#c994c7", "#dd1c77"]
oranges = ["#fff7bc", "#fec44f", "#d95f0e"]


d3.json("http://127.0.0.1:8000/static/webics/js/lena.json", function(error, img) {
  var dx = img[0].length,
      dy = img.length;

  // Fix the aspect ratio.
  var ka = dy / dx, kb = height / width;
  if (ka < kb) height = width * ka;
  else width = height / ka;

  var x = d3.scale.linear()
      .domain([0, dx])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([0, dy])
      .range([height, 0]);

  var color = d3.scale.linear()
      .domain([0, 127, 255])
      .range(reds);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("top")
      .ticks(20);

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("right");

  d3.select("body").append("canvas")
      .attr("width", dx)
      .attr("height", dy)
      .style("width", width + "px")
      .style("height", height + "px")
      .call(drawImage);

  var svg = d3.select("body").append("svg")
      .attr("width", width)
      .attr("height", height);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .call(removeZero);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .call(removeZero);

  // Compute the pixel colors; scaled by CSS.
  function drawImage(canvas) {
    var context = canvas.node().getContext("2d"),
        image = context.createImageData(data.h_axis.length, data.v_axis.length);

    for (var y = 0, p = -1; y < data.values.length; ++y) {
      for (var x = 0; x < data.values[0].length; ++x) {
        var c = d3.rgb(color(data.values[y][x]));
        image.data[++p] = c.r;
        image.data[++p] = c.g;
        image.data[++p] = c.b;
        image.data[++p] = 255;
      }
    }

    context.putImageData(image, 0, 0);
  }

  function removeZero(axis) {
    axis.selectAll("g").filter(function(d) { return !d; }).remove();
  }

  var line;
  var rect;
  var rect_x;
  var rect_y;
  var vis = d3.select("body").append("svg")
      .on("mousedown", mousedown)
      .on("mouseup", mouseup);

  function mousedown() {
      var m = d3.mouse(this);
      rect_x = m[0];
      rect_y = m[1];
      rect = vis.append("rect")
          .attr("x", m[0])
          .attr("y", m[1])
          .attr("width", 0)
          .attr("height", 0);

      var text = svg.selectAll("text")
                  .data(m)
                  .enter()
                  .append("text");

      var textLabels = text
                 .attr("x", width-100)
                 .attr("y", height-25)
                 .text( function (m) { return "( " + m[0] + ", " + m[1] +" )"; })
                 .attr("font-family", "sans-serif")
                 .attr("font-size", "20px");

      vis.on("mousemove", mousemove);

      
  }

  function mousemove() {
      var m = d3.mouse(this);
      rect.attr("class", "rect");
      if (m[0]-rect_x>0){
        rect.attr("x", rect_x);
        rect.attr("width", m[0]-rect_x);
      }
      else {
        rect.attr("x", m[0]);
        rect.attr("width", rect_x-m[0]);
      }
      if (m[1]-rect_y>0){
        rect.attr("y", rect_y);
        rect.attr("height", m[1]-rect_y);
      }
      else {
        rect.attr("y", m[1]);
        rect.attr("height", rect_y-m[1]);
      }

          
  }

  function mouseup() {
      vis.on("mousemove", null);
  }
});