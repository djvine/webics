var http = require('http'),
io = require('socket.io');

var server = http.createServer(function(request, response) {
  response.writeHeader(200, {"Content-Type": "text/html"});
  response.end();
}).listen(8001);
//and replace var socket = io.listen(1223, "1.2.3.4"); with:
var socket = io.listen(server);
var people = {};
var people_groups = {};
var groups = {
    '2idb': [],
    '2idd': [],
    '2ide': []
};

socket.on("connection", function (client) {
    client.on("join", function(name, beamline){
        people[client.id] = name;
        if (beamline != 'broadcast'){
            people_groups[client.id] = beamline;
            groups[beamline].push(client);
        }
        
        client.emit("update", "You have connected to the server.");
        if (groups[beamline].length>1){
            for (var i = groups[beamline].length - 1; i >= 0; i--) {
                groups[beamline][i].emit("update", name + " has joined the server.");
                groups[beamline][i].emit("update-people", people);
            };
        }
    });

    client.on("send", function(msg, beamline){
        if (beamline=='broadcast'){
            socket.sockets.emit("chat", people[client.id], people_groups[client.id], msg);
        }
        else {
            for (var i = groups[beamline].length - 1; i >= 0; i--) {
                groups[beamline][i].emit("chat", people[client.id], people_groups[client.id],  msg);
            };
        }
        
    });

    client.on("disconnect", function(){
        delete groups[people_groups[client.id]];
        delete people_groups[client.id];
        socket.sockets.emit("update", people[client.id] + " has left the server.");
        delete people[client.id];
        socket.sockets.emit("update-people", people);
    });
});