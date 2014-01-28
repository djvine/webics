var http = require('http'),
io = require('socket.io');
var redis = require('socket.io/node_modules/redis');
var server = http.createServer(function(request, response) {
  response.writeHeader(200, {"Content-Type": "text/html"});
  response.end();
}).listen(8001);

var socket = io.listen(server);
var chat = socket.of('/chat');
var scan = socket.of('/scan')
// Chat
var people = {};
var beamline_groups = {};
// Scans
var scans = {}  // Record which client id is subscribed to each beamline
var get_realtime = {} // Record whether client is subscribed to live updates

chat.on("connection", function (client) {
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
            chat.emit("update", name + "(" + beamline +  ") has joined the server.");
            chat.emit("update-people", people);
        }
    });

    client.on("send", function(msg, beamline){
        if (beamline=='broadcast'){
            chat.emit("chat", people[client.id], beamline, msg);
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
        chat.emit("update", people[client.id] + " has left the server.");
        delete people[client.id];
        chat.emit("update-people", people);
    });
});


scan.on("connection", function(client) {
    //Grab message from Redis and send to client

    client.on("room", function(beamline){
        client.join(beamline);
        client.emit("update", "You have joined at "+beamline);
        scans[client.id] = beamline;
        get_realtime[client.id] = 1;
        //Redis
        var sub = redis.createClient();
        sub.subscribe(beamline);
        sub.on('message', function(channel, message){
            json_ob = JSON.parse(message);
            if (json_ob.hasOwnProperty('new_scan')){
                client.emit('new_data', message);
            }
            else if (json_ob.hasOwnProperty('update_data')){
                client.emit("update_data", message);
            }
        });

    });

    client.on('scan_select', function (beamline, scan_id){
        // Asking for latest scan?
        client.emit('update', 'getting new data');
    });


    client.on("disconnect", function(){
        delete scans[client.id];
        delete get_realtime[client.id];
        scan.emit('update', "Somebody left.");
    });
});