$(document).ready(function(){
        var socket = io.connect("127.0.0.1:8001");
        $("#chat").hide();
        $("#name").focus();
        $("form").submit(function(event){
            event.preventDefault();
        });
        // user clicks join
        $("#join").click(function(){
            var name = $("#name").val();
            if (name != "") {
                console.log(beamline);
                socket.emit("join", name, beamline);
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
                    socket.emit("join", name, beamline);
                    ready = true;
                    $("#login").detach();
                    $("#chat").show();
                    $("#msg").focus();
                }
            }
        });

        socket.on("update", function(msg) {
            if(ready)
                $("#msgs").append("" + msg + "<br>");
        })

        socket.on("update-people", function(people){
            if(ready) {
                $("#people").empty();
                $.each(people, function(clientid, name) {
                    $('#people').append("" + name + " ");
                });
            }
        });

        socket.on("chat", function(who, beamline, msg){
            if(ready) {
                $("#msgs").append("" + who + "(" + beamline + ")" + " says: " + msg + "<br>");
                $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
            }
        });

        socket.on("disconnect", function(){
            $("#msgs").append("The server is not available");
            $("#msg").attr("disabled", "disabled");
            $("#send").attr("disabled", "disabled");
        });


        $("#send").click(function(){
            var msg = $("#msg").val();
            socket.emit("send", msg, beamline);
            $("#msg").val("");
        });

        $("#msg").keypress(function(e){
            if(e.which == 13) {
                var msg = $("#msg").val();
                socket.emit("send", msg, beamline);
                $("#msg").val("");
            }
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