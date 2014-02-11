$(document).ready(function(){
	var cal = new CalHeatMap();
	cal.init({
	itemSelector: "#cal-heatmap",
	domain: "year",
	subDomain: "day",
	data: "datas-years.json",
	start: new Date(2000, 0),
	cellSize: 10,
	range: 1,
	legend: [20, 40, 60, 80]
});
});