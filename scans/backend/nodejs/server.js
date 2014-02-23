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
var scans = {};  // Record which client id is subscribed to each beamline
var clients = {};
var get_realtime = {}; // Record whether client is subscribed to live updates
var scan_data_cache = {}; // Cache the "new_scan" data for each beamline to send to clients joining during a scan.

chat.on("connection", function (client) {
    client.on("join", function(name, beamline){
        people[client.id] = name + " (" + beamline +  ")";
        
        try{
            beamline_groups[beamline].push(client);   
        }
        catch (err) {
            beamline_groups[beamline] = [client];
        }
        client.emit("update", "You have connected to the server.");
        chat.emit("update", name+" has joined the server.");
        chat.emit("update-people", people);
        
    });

    client.on("send", function(msg, audience){
        if (audience=='broadcast'){
            chat.emit("chat", people[client.id], msg);
        }
        else {
            for (var i = beamline_groups[audience].length - 1; i >= 0; i--) {
                beamline_groups[audience][i].emit("chat", people[client.id],  msg);
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

/*
Scan listens for:
    * room
    * scan_select
Scan emits:
    * new_scan
    * update_scan
    * scan_completed
*/

scan.on("connection", function(client) {
    //Grab message from Redis and send to client

    client.on("room", function(beamline){
        client.join(beamline);
        client.emit("update", "You have joined at "+beamline);
        scans[client.id] = beamline;
        clients[client.id] = client;
        if (scan_data_cache[beamline]){
            client.emit('new_scan', scan_data_cache[beamline]);
        }
        get_realtime[client.id] = 1;

        //Redis
        var sub = redis.createClient();
        sub.subscribe(beamline);
        sub.on('message', function(channel, message){
            json_ob = JSON.parse(message);
            if (json_ob.hasOwnProperty('new_scan')){
                scan_data_cache[beamline] = json_ob['new_scan'];
                if (get_realtime[client.id]==1) { // Subscribed to realtime updates
                    client.emit('new_scan', json_ob['new_scan']);
                }
                else { // Not subscribed to realtime updates
                    client.emit('update_scan_history', json_ob['new_scan'])
                }
            }
            else if (json_ob.hasOwnProperty('update_scan')){
                if (get_realtime[client.id]==1) { // Subscribed to realtime updates
                    client.emit("update_scan", json_ob['update_scan']);
                }
                else { // Not subscribed to realtime updates
                    client.emit('update_scan_history_norealtime', json_ob['update_scan'])
                }
            }
            else if (json_ob.hasOwnProperty('completed_scan')){
                client.emit('completed_scan', json_ob['completed_scan']);
                delete scan_data_cache[beamline];
            }
        });

    });

    client.on('history_request', function (beamline, scan_id, subscribe_to_realtime){
        // Asking for latest scan?
        get_realtime[client.id] = subscribe_to_realtime;
        client.emit('update', 'client requested historical data');
        var hist_request_client = redis.createClient();
        hist_request_client.publish('hist_request', [beamline, scan_id, client.id]);

    });

    client.on('subscribe_to_realtime', function (){
        // Asking for latest scan?
        get_realtime[client.id] = 1;
    });

    client.on("disconnect", function(){
        delete scans[client.id];
        delete get_realtime[client.id];
        delete clients[client.id];
        scan.emit('update', "Somebody left.");
    });
    
});

var hist_reply_client = redis.createClient();
hist_reply_client.subscribe('hist_reply');
hist_reply_client.on('message', function(channel, message){
    json_ob = JSON.parse(message);
    clients[json_ob['client_id']].emit('hist_reply', json_ob['data']);
});