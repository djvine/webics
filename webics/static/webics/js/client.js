$(document).ready(function(){
        var socket = io.connect("127.0.0.1:8001");
        var chatSocket = io.connect("127.0.0.1:8001/chat");
        var scanSocket = io.connect("127.0.0.1:8001/scan");
        scanSocket.emit("room", beamline);
        $("#chat").hide();
        $("#name").focus();
        $("form").submit(function(event){
            event.preventDefault();
        });
        // user clicks join
        $("#join").click(function(){
            var name = $("#name").val();
            if (name != "") {
                chatSocket.emit("join", name, beamline);
                $("#login").detach();
                $("#chat").show();
                $("#msg").focus();
                ready = true;
            }
        });
        // user presses enter
        $("#name").keypress(function(e){
            if(e.which == 13) {
                var name = $("#name").val();
                if (name != "") {
                    chatSocket.emit("join", name, beamline);
                    ready = true;
                    $("#login").detach();
                    $("#chat").show();
                    $("#msg").focus();
                }
            }
        });

        chatSocket.on("update", function(msg) {
            if(ready)
                $("#msgs").append("" + msg + "<br>");
        });

        chatSocket.on("update-people", function(people){
            if(ready) {
                $("#people").empty();
                $.each(people, function(clientid, name) {
                    $('#people').append("" + name + " ");
                });
            }
        });

        chatSocket.on("chat", function(who, beamline, msg){
            if(ready) {
                $("#msgs").append("" + who + "(" + beamline + ")" + " says: " + msg + "<br>");
                $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
            }
        });

        chatSocket.on("disconnect", function(){
            $("#msgs").append("The server is not available");
            $("#msg").attr("disabled", "disabled");
            $("#send").attr("disabled", "disabled");
        });


        $("#send").click(function(){
            var msg = $("#msg").val();
            chatSocket.emit("send", msg, beamline);
            $("#msg").val("");
        });

        $("#msg").keypress(function(e){
            if(e.which == 13) {
                var msg = $("#msg").val();
                chatSocket.emit("send", msg, bDeamline);
                $("#msg").val("");
            }
        });

        $("#").click(function(){
            var name = $("#name").val();
            if (name != "") {
                chatSocket.emit("join", name, beamline);
                $("#login").detach();
                $("#chat").show();
                $("#msg").focus();
                ready = true;
            }
        });

        scanSocket.on("update", function(msg) {
            console.log(msg);
        });

        var update_scan_history = function (new_data, scan_completed){
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
                
                s = '<tr><td><button type="button" class="'+class_name+'"" id="'+new_data['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button></td><td>'+new_data['scan']['ts']+'</td><td>'+ new_data['scan']['scan_id'] +'</td>';

                for (var i = new_data['scan_hist'].length - 1; i >= 0; i--) {
                    s+='<td>'+new_data['scan_hist'][i]['completed']+'/'+new_data['scan_hist'][i]['requested']+'</td>';
                };

                s+='</tr>';
                $("#scan_history").prepend(s);
                document.getElementById('scan_history').rows[1].className = 'highlight';
            }
            else if (scan_completed==1){
                document.getElementById('scan_history').rows[1].className = '';
                s='<button type="button" class="'+class_name+'"" id="'+new_data['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button>'
                document.getElementById('scan_history').rows[1].cells[0].innerHTML = s;
                for (var i = 0; i<new_data['scan_hist'].length; i++) {
                    s = new_data['scan_hist'][i]['completed']+'/'+new_data['scan_hist'][i]['requested'];
                    document.getElementById('scan_history').rows[1].cells[3+i].innerHTML = s;
                };
            }

        }

        var begin_new_scan = function(data){
            known_n_rows = 1;
            n_rows = -1; // Don't count 'x' element
            for (key in data['scan_data']){
                n_rows+=1;
            }
            current_row = 0;
            data1 = data['scan_data'];
            var new_dets = [];
            selected_detectors.forEach(function(element, i){
                var idx = data['scan_dets'].indexOf(element);
                if (idx>-1){ // A detector is selected which DOES exist in the new dataset so keep it
                    new_dets.push(element);
                }
            })
            selected_detectors = new_dets;
            updateActiveDetectors(data['scan_dets']);
            console.log(data['scan_data']);
            l1.updateData(data['scan_data'], current_row, selected_detectors);
            update_row_button_state();
        }

        var update_scan_data = function(data){
            
            n_rows = -1; // Don't count 'x' element
            for (key in data['scan_data']){
                
                n_rows+=1;
            }
            
            if (known_n_rows!=n_rows){ // a new row is available
                
                // Are we displaying latest row?
                if (current_row+1==known_n_rows){//Yes
                    current_row+=1
                    document.getElementById('current_row').innerHTML=(current_row+1)+'/'+n_rows;
                }
                known_n_rows = n_rows;
            }
            if (current_row<0 || current_row>=n_rows){
                current_row = 0;
            }
            data1 = data['scan_data'];
            l1.updateData(data['scan_data'], current_row, selected_detectors);
            update_row_button_state();
        }

        scanSocket.on("new_scan", function(new_data){
            console.log('new_scan received');
            update_scan_history(new_data, 0);
            begin_new_scan(new_data);       
        });

        scanSocket.on("update_scan_history", function(new_data){
            console.log('update scan history received');
            update_scan_history(new_data, 0);
        });

        scanSocket.on("update_scan", function(update_data){
            console.log('update scan received');
            update_scan_data(update_data);
        });
        scanSocket.on("scan_completed", function(new_data){
            console.log('scan completed');
            update_scan_history(new_data, 1);
        });
        scanSocket.on('hist_data_reply', function(new_data){
            console.log('Hist data reply received at client.')
            begin_new_scan(new_data);
        });

        $(document).on("click", ".scan_sel", function(){
            console.log(this.id);
            var idx = document.getElementById('scan_history').rows[1].cells[0].childNodes[0].className.indexOf('success');
            var subscribe_to_realtime = 0;
            if (idx>-1){
                subscribe_to_realtime = 1;
            }

            scanSocket.emit('scan_select', beamline, this.id, subscribe_to_realtime);
            [].forEach.call(document.getElementsByClassName('scan_sel'), function (element) {
                element.className = "scan_sel btn btn-primary btn-xs";
            })
            this.className = "scan_sel btn btn-success btn-xs";
        });

    });

    
var old_beamline = "";
var onbroadcast = function(button_id){
    
    if (document.getElementById(button_id).className == "btn btn-default"){
        document.getElementById(button_id).className = "btn btn-default active";
        old_beamline = beamline;
        beamline = button_id;
    }
    else {
        document.getElementById(button_id).className = "btn btn-default";
        beamline = old_beamline;
        }
    console.log(beamline);

}

