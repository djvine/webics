#!/bin/bash 
if screen -list | grep -q "webics";  then
    echo "Webics screen session exists"
else:
    echo "Creating screen session webics"
    screen -d -m -S webics -t webics
