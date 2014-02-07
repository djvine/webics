var n_rows, known_n_rows, current_row;

$(document).ready(function(){
	current_row = 0;
	n_rows = Object.keys(data['scan_data']).length - 2;
	document.getElementById('current_row').innerHTML=1+'/'+n_rows;

	var l1 = new LinePlot({containerId: 'line_plot', data: data['scan_data']});
	update_row_button_state()

	$(document.body).on('Scan:reply', function(event, new_data) {
		current_row = 0;
    	console.log('Got scan reply');
    	data = new_data;
    	l1.updateData(new_data['scan_data'], current_row, selected_detectors);
    	update_row_button_state()
	});

	$(document.body).on('Scan:begin', function(event, new_data){
		known_n_rows = 1;
        n_rows = Object.keys(data['scan_data']).length-2;
        document.getElementById('current_row').innerHTML=(current_row+1)+'/'+n_rows;
        current_row = 0;
        data = new_data;
        l1.updateData(data['scan_data'], current_row, selected_detectors);
        update_row_button_state();
	});

	$(document.body).on('Scan:update', function(event, new_data){
		n_rows = Object.keys(data['scan_data']).length-2;
            
        if (known_n_rows!=n_rows){ // a new row is available
            
            // Are we displaying latest row?
            if (current_row+1==known_n_rows){//Yes
                current_row+=1
                
            }
            known_n_rows = n_rows;
        }
        if (current_row<0 || current_row>=n_rows){
            current_row = 0;
        }
        data = new_data;
        l1.updateData(data['scan_data'], current_row, selected_detectors);
        update_row_button_state();
	});

	$(document.body).on('DetButtons:selection', function(event, param) {
    	l1.updateData(data['scan_data'], current_row, selected_detectors);
	});
	$(document.body).on('DetButtons:deselection', function(event, param) {
    	l1.updateData(data['scan_data'], current_row, selected_detectors);
	});

	$(document).on("click", "#increment_row", function(){
	    if (current_row+1<n_rows){
			current_row++;
			
			update_row_button_state()
			l1.updateData(data['scan_data'], current_row, selected_detectors);
		}	
	});

	$(document).on("click", "#decrement_row", function(){
	    if (current_row-1>=0){
			current_row--;
			
			update_row_button_state()
			l1.updateData(data['scan_data'], current_row, selected_detectors);
		}
	});
})



/*
 *  This function changes the row button disabled state depending on how many rows are available.
 */
var update_row_button_state = function(){
    n_rows = Object.keys(data['scan_data']).length-2; // Don't count 'x' & 'y' elements
	document.getElementById('current_row').innerHTML=(current_row+1)+'/'+n_rows;
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
