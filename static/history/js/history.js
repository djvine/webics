function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

var update_scan_history = function (scan_data, scan_completed){

	// Transfer button state to latest scan (if appropriate)
    var idx = document.getElementById('scan_history').rows[1].cells[0].childNodes[0].className.indexOf('success');
    if (idx>-1){
        class_name = "scan_sel btn btn-success btn-xs";
        [].forEach.call(document.getElementsByClassName('scan_sel'), function (element) {
            element.className = "scan_sel btn btn-primary btn-xs";
        })
    }
    else {
        class_name = "scan_sel btn btn-primary btn-xs";
    }
    console.log(scan_data);
    
    if (scan_completed==0){
        
        s = '<tr><td><button type="button" class="'+class_name+'"" id="'+scan_data['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button></td><td>'+scan_data['scan']['ts_str']+'</td><td>'+ scan_data['scan']['scan_id'] +'</td>';

        for (var i = scan_data['scan_hist'].length - 1; i >= 0; i--) {
            s+='<td>'+scan_data['scan_hist'][i]['completed']+'/'+scan_data['scan_hist'][i]['requested']+'</td>';
        };

        s+='</tr>';
        $("#scan_history").prepend(s);
        document.getElementById('scan_history').rows[1].className = 'highlight';
    }
    else if (scan_completed==1){
        document.getElementById('scan_history').rows[1].className = '';
        s='<button type="button" class="'+class_name+'"" id="'+scan_data['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button>'
        document.getElementById('scan_history').rows[1].cells[0].innerHTML = s;
        for (var i = 0; i<scan_data['scan_hist'].length; i++) {
            s = scan_data['scan_hist'][i]['completed']+'/'+scan_data['scan_hist'][i]['requested'];
            document.getElementById('scan_history').rows[1].cells[3+i].innerHTML = s;
        };
    }

}

$(document).on("click", ".scan_sel", function(){
    
    if (this.id==document.getElementById('scan_history').rows[1].cells[2].innerHTML){
        subscribe_to_realtime = 1;
    }
    else{
        subscribe_to_realtime = 0;
    }

    if (this.id==document.getElementById('scan_history').rows[1].cells[2].innerHTML) { // asking for latest scan
        if (hasClass(document.getElementById('scan_history').rows[1], 'highlight')) { // there is a scan currently running
            $(document.body).trigger('History:subscribe_to_realtime', [beamline]);
        }
        else {
            $(document.body).trigger('History:request', [beamline, this.id, subscribe_to_realtime]);
        }
    }
    else {
        $(document.body).trigger('History:request', [beamline, this.id, subscribe_to_realtime]);
    }

    [].forEach.call(document.getElementsByClassName('scan_sel'), function (element) {
        element.className = "scan_sel btn btn-primary btn-xs";
    })
    this.className = "scan_sel btn btn-success btn-xs";
});


$(document).ready(function(){

	$(document.body).on('Scan:updateHistory', function(event, param) {
    	console.log('Update scan history');
    	update_scan_history(param, 0);
	});

	$(document.body).on('Scan:begin', function(event, param) {
    	console.log('Scan begin');
    	update_scan_history(param, 0);
	});
	
	$(document.body).on('Scan:end', function(event, param) {
    	console.log('Scan end');
    	update_scan_history(param, 1);
	});

})