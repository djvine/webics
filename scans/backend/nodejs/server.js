var http = require('http'),
io = require('socket.io');

var server = http.createServer(function(request, response) {
  response.writeHeader(200, {"Content-Type": "text/html"});
  response.end();
}).listen(8001);
//and replace var socket = io.listen(1223, "1.2.3.4"); with:
var socket = io.listen(server);
var people = {};
var beamline_groups = {};


socket.on("connection", function (client) {
    client.on("join", function(name, beamline){
        people[client.id] = name;
        if (beamline != 'broadcast'){
            try{
                beamline_groups[beamline].push(client);   
            }
            catch (err) {
                beamline_groups[beamline] = [client];
            }
            client.emit("update", "You have connected to the server.");
            socket.sockets.emit("update", name + "(" + beamline +  ") has joined the server.");
            socket.sockets.emit("update-people", people);
        }
    });

    client.on("send", function(msg, beamline){
        if (beamline=='broadcast'){
            socket.sockets.emit("chat", people[client.id], beamline, msg);
        }
        else {
            for (var i = beamline_groups[beamline].length - 1; i >= 0; i--) {
                beamline_groups[beamline][i].emit("chat", people[client.id], beamline,  msg);
            };
        }
        
    });

    client.on("disconnect", function(){
        for(var beamline in beamline_groups){
            var index = beamline_groups[beamline].indexOf(client);
            if (index>-1){
                beamline_groups[beamline].splice(index, 1);
            }
        } 
        socket.sockets.emit("update", people[client.id] + " has left the server.");
        delete people[client.id];
        socket.sockets.emit("update-people", people);
    });
});