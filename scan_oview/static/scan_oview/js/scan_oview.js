$(document).ready(function(){
	var cal = new CalHeatMap();
	cal.init({
		itemSelector: "#cal-heatmap",
		domain: "month",
		subDomain: "day",
		data: data,
		start: new Date(Math.abs(new Date()-345*24*3600*1000)),
		cellSize: 10,
		range: 12,
		legend: [5, 10, 15, 20],
		nextSelector: "#domainDynamicDimension-next",
		previousSelector: "#domainDynamicDimension-previous"
	});
});