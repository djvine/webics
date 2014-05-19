$(document).ready(function(){
    //var chatSocket = io.connect("127.0.0.1:8001/chat");
    var chatSocket = io.connect("164.54.113.91:8001/chat");
    var audience = beamline;
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

    chatSocket.on("chat", function(who, msg){
        if(ready) {
            $("#msgs").append("" + who + " says: " + msg + "<br>");
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
        chatSocket.emit("send", msg, audience);
        $("#msg").val("");
    });

    $("#msg").keypress(function(e){
        if(e.which == 13) {
            var msg = $("#msg").val();
            chatSocket.emit("send", msg, audience);
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

    $(".chat-audience a").click(function(){
        audience = this.id;
        console.log(this.id);
        if (this.id=='broadcast'){
            s = 'All';
        }
        else {
            s = this.id;
        }
        document.getElementById('audience-button').innerHTML = "Audience: "+s;
    });
});
