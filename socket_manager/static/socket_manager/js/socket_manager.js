$(document).ready(function(){
    var scanSocket = io.connect("127.0.0.1:8001/scan");
    scanSocket.emit("room", beamline);

    // For debugging
    scanSocket.on("update", function(msg) {
        console.log(msg);
    });

    scanSocket.on('new_scan', function(data){
    	$(document.body).trigger('Scan:begin', data);
    	console.log('new scan')
    });

    scanSocket.on('update_scan', function(data){
    	$(document.body).trigger('Scan:update', data)
    	console.log('update scan')
    });

    scanSocket.on('completed_scan', function(data){
    	$(document.body).trigger('Scan:end', data)
    	console.log('completed scan')
    });

    scanSocket.on('update_scan_history', function(data){
    	$(document.body).trigger('Scan:updateHistory', data)
    	console.log('update history')
    });

    scanSocket.on('hist_reply', function(data){
    	$(document.body).trigger('Scan:reply', data)
    	console.log('got reply')
    });

    $(document.body).on('History:request', function(event, beamline, scan_id, subscribe_to_realtime) {
    	console.log('Sending history request to scanSocket');
    	scanSocket.emit('history_request', beamline, scan_id, subscribe_to_realtime);
	});

    $(document.body).on('History:subscribe_to_realtime', function(event, beamline){
        scanSocket.emit('subscribe_to_realtime');
    });

});