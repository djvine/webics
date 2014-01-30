var active_detectors = [];
var selected_detectors = [];
var n_rows = 1;
var known_n_rows = 1; // Used to decide if a new row has arrived
var current_row = 0;

function zeroPad(num, places) {
	var zero = places - num.toString().length + 1;
	return Array(+(zero > 0 && zero)).join("0") + num;
}

function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

/*
 *  This function enables or disables the detector select buttons and sets the active_detectors array
 */
updateActiveDetectors = function(det_names){
	selected_detectors = [];
	for (var i=1;i<71;i++)
	{ 
		document.getElementById("D"+zeroPad(i,2)).className = "btn btn-primary btn-xs disabled";
	}
	
	det_names.forEach(function(element, index){
		if (index==0){
			document.getElementById(element).className = "btn btn-success btn-xs";
			selected_detectors.push(element);
		}
		else {
			document.getElementById(element).className = "btn btn-primary btn-xs";
		}
	})
}

/*
 *  This function is called when a detector select button is pressed. It:
 * 		* changes button state
 *		* updates selected_detectors
 *		* updates line chart
 */
var toggle_state = function (button_id)
{
	if (hasClass(document.getElementById(button_id), 'btn-primary')){ // Not Selected
		document.getElementById(button_id).className = "btn btn-success btn-xs";
		var index = selected_detectors.indexOf(button_id);
		if (index == -1){
			selected_detectors.push(button_id);
		}
	}
	else {
		if (selected_detectors.length > 1){
			document.getElementById(button_id).className = "btn btn-primary btn-xs";
			var index = selected_detectors.indexOf(button_id);
			if (index > -1) {
	    		selected_detectors.splice(index, 1);
			}
		}
	}
	l1.updateData(data1, current_row, selected_detectors);
	console.log(selected_detectors);
}


/*
 *  This function is called when a row button is pressed. It:
 *		* updates the current_row variable. 
 */
var change_row = function (button_id){
	if (button_id=='increment_row'){
		if (current_row+1<n_rows){
			current_row++;
			document.getElementById('current_row').innerHTML=(current_row+1)+'/'+n_rows;
		}	
	}
	else {
		if (current_row-1>=0){
			current_row--;
			document.getElementById('current_row').innerHTML=(current_row+1)+'/'+n_rows;
		}
	}
	update_row_button_state()
	l1.updateData(data1, current_row, selected_detectors);
}

/*
 *  This function changes the row button disabled state depending on how many rows are available.
 */
var update_row_button_state = function(){
    n_rows = -1; // Don't count 'x' element
    for (key in data1){
        n_rows+=1;
    }


	if (current_row>=n_rows-1){
		//Disable increment button
		document.getElementById('increment_row').className = "btn btn-default btn-xs disabled"
	} else{
		document.getElementById('increment_row').className = "btn btn-default btn-xs"
	}
	if (current_row<=0){
		//Disable increment button
		document.getElementById('decrement_row').className = "btn btn-default btn-xs disabled"
	} else{
		document.getElementById('decrement_row').className = "btn btn-default btn-xs"
	}
}