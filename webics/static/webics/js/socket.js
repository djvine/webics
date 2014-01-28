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

        var update_scan_history = function (new_data){
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

            new_data = JSON.parse(new_data)['new_scan'];

            s = '<tr><td><button type="button" class="'+class_name+'"" id="'+new_data['scan']['scan_id']+'"><span class="glyphicon glyphicon-play"></span></button></td><td>'+new_data['scan']['ts']+'</td><td>'+ new_data['scan']['scan_id'] +'</td>'

            for (var i = new_data['scan_hist'].length - 1; i >= 0; i--) {
                s+='<td>'+new_data['scan_hist'][i]['completed']+'/'+new_data['scan_hist'][i]['requested']+'</td>';
            };

            s+='</tr>'
            $("#scan_history").prepend(s)
        }

        scanSocket.on("new_data", function(new_data){
            console.log(new_data);
            
            update_scan_history(new_data);         



        });

        scanSocket.on("update_data", function(msg){
            console.log(msg);
        });

        scanSocket.on("new_scan", function(msg){
            console.log(msg);
        });

        $(".scan_sel").click(function(){
            console.log(this.id);
            // if currently selected button was re-selected do nothing

            scanSocket.emit('scan_select', beamline, this.id);
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

