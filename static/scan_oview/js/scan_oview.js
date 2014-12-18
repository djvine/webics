$(document).ready(function(){
	var cal = new CalHeatMap();
	cal.init({
		itemSelector: "#cal-heatmap",
		domain: "month",
		subDomain: "day",
		data: data,
		start: new Date(Math.abs(new Date()-11*30*24*3600*1000)),
		cellSize: 10,
		range: 12,
		tooltip: true,
		legend: [5, 10, 15, 20],
		highlight: "now",
		nextSelector: "#domainDynamicDimension-next",
		previousSelector: "#domainDynamicDimension-previous"
	});
});
