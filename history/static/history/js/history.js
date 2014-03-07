function hasClass( elem, klass ) {
     return (" " + elem.className + " " ).indexOf( " "+klass+" " ) > -1;
}

var date_event = 0;

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
    	update_scan_history(param, 0);
	});

    $(document.body).on('Scan:newHistory', function(event, param) {
        // update history
    });

	$(document.body).on('Scan:begin', function(event, param) {
    	update_scan_history(param, 0);
	});
	
	$(document.body).on('Scan:end', function(event, param) {
    	update_scan_history(param, 1);
	});

    $(document.body).on('Scan:update', function(event, param){
        data = param;
        hist_known_n_rows = Object.keys(data['scan_data']).length-2;
        for (var i = 0; i<data['scan_hist'].length; i++) {
            if (i==0){
                s = data['scan_data'][hist_known_n_rows-1][0].values.length+'/'+data['scan_hist'][0]['requested'];
            }
            else {
                s = (hist_known_n_rows-1)+'/'+data['scan_hist'][i]['requested'];
            }
            document.getElementById('scan_history').rows[1].cells[3+i].innerHTML = s;
        };
    });

    $(document.body).on('Scan:updateHistoryNoRealtime', function(event, param){
        data = param;
        hist_known_n_rows = Object.keys(data['scan_data']).length-2;
        for (var i = 0; i<data['scan_hist'].length; i++) {
            if (i==0){
                s = data['scan_data'][hist_known_n_rows-1][0].values.length+'/'+data['scan_hist'][0]['requested'];
            }
            else {
                s = (hist_known_n_rows-1)+'/'+data['scan_hist'][i]['requested'];
            }
            document.getElementById('scan_history').rows[1].cells[3+i].innerHTML = s;
        };
    });

    jQuery(function($) {
        $('#datepick-container .input-daterange').datepicker({
            format: "mm-dd-yyyy",
            endDate: "today",
            todayBtn: "linked",
            autoclose: true,
            todayHighlight: true
        });

        $('#datepick-container .input-daterange').datepicker()
            .on('changeDate', function(e){
                // Get start & end date
                start_date = document.getElementsByName('start')[0].value;
                end_date = document.getElementsByName('end')[0].value;
                if (e['timeStamp']-date_event<50){
                    date_event = e['timeStamp'];
                    return;
                }
                
                if (start_date == ""){
                    start_date = new Date();
                }
                else {
                    start_date = new Date(start_date);
                }
                if (end_date == ""){
                    if (start_date==""){
                        end_date = new Date();
                    }
                    else {
                        end_date = new Date();
                        end_date.setDate(start_date.getDate()+1);
                    }
                }
                else {
                    end_date = new Date(end_date);
                }
                if (end_date<start_date){
                    end_date.setDate(start_date.getDate()+1);
                }
                $(document.body).trigger('History:requestNewHistory', [beamline, start_date, end_date]);
                date_event = e['timeStamp'];

            });

    });

    $(document.body).on('Scan:new_hist_reply', function(event, data){
        data = data['data'];
        var tbl = document.getElementById("scan_history");
        tbl.innerHTML = "";
        if (data.length==0){
            row = tbl.insertRow(0);
            alertdiv = document.createElement('div');
            alertdiv.setAttribute('class', 'alert alert-danger');
            alertdiv.innerHTML = "<strong>Oh snap!</strong> Wasn't able to retrieve any scan data."
            row.appendChild(alertdiv);
        }
        else {
            var theader = tbl.createTHead();

            var hrow = theader.insertRow(0);
            var hcell1 = hrow.insertCell(0);
            var hcell2 = hrow.insertCell(1);
            var hcell3 = hrow.insertCell(2);
            var hcell4 = hrow.insertCell(3);
            var hcell5 = hrow.insertCell(4);

            hcell1.innerHTML = '<b>Show</b>';
            hcell2.innerHTML = '<b>Time</b>';
            hcell3.innerHTML = '<b>Scan ID</b>';
            hcell4.innerHTML = '<b>1D</b>';
            hcell5.innerHTML = '<b>2D</b>';

            var tbody = tbl.appendChild(document.createElement('tbody'));
            console.log(data);
            console.log(data.length);
            for (var i = data.length - 1; i >= 0; i--) {
                
                row = tbody.insertRow(0);

                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
                var cell3 = row.insertCell(2);
                var cell4 = row.insertCell(3);
                var cell5 = row.insertCell(4);

                if (i==0){
                    s='btn-success';
                }
                else {
                    s='btn-primary';
                }

                cell1.innerHTML = '<button type="button" class="scan_sel btn '+s+' btn-xs" id="'+data[i]['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button>'
                cell2.innerHTML = data[i]['scan']['ts'];
                cell3.innerHTML = data[i]['scan']['scan_id'];
                cell4.innerHTML = data[i]['scan_hist'][0]['completed']+'/'+data[i]['scan_hist'][0]['requested'];
                if (data[i]['scan_hist'].length>1){
                    cell4.innerHTML = data[i]['scan_hist'][1]['completed']+'/'+data[i]['scan_hist'][1]['requested'];
                }
            };
        }
        

    });
    
})