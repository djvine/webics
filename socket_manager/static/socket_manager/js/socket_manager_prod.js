$(document).ready(function(){
    var scanSocket = io.connect("lemon.xray.aps.anl.gov:8001/scan");
    scanSocket.emit("room", beamline);

    // For debugging
    scanSocket.on("update", function(msg) {
        console.log(msg);
    });

    scanSocket.on('new_scan', function(data){
    	$(document.body).trigger('Scan:begin', data);
    });

    scanSocket.on('update_scan', function(data){
    	$(document.body).trigger('Scan:update', data)
    });

    scanSocket.on('completed_scan', function(data){
    	$(document.body).trigger('Scan:end', data)
    });

    scanSocket.on('update_scan_history', function(data){
    	$(document.body).trigger('Scan:updateHistory', data)
    });

    scanSocket.on('update_scan_history_norealtime', function(data){
        $(document.body).trigger('Scan:updateHistoryNoRealtime', data)
    });

    scanSocket.on('hist_reply', function(data){
    	$(document.body).trigger('Scan:reply', data)
    });

    scanSocket.on('hist_new_hist_reply', function(data){
        $(document.body).trigger('Scan:new_hist_reply', {'data': data})
    });

    $(document.body).on('History:request', function(event, beamline, scan_id, subscribe_to_realtime) {
    	scanSocket.emit('history_request', beamline, scan_id, subscribe_to_realtime);
	});

    $(document.body).on('History:requestNewHistory', function(event, beamline, start_date, end_date) {
        console.log('emitting request');
        scanSocket.emit('history_request_new_history', beamline, start_date, end_date);
    });

    $(document.body).on('History:subscribe_to_realtime', function(event, beamline){
        scanSocket.emit('subscribe_to_realtime');
    });

});
