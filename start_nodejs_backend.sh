#!/bin/bash -e
if [ $WEBICS_HOME ]; then
    echo "here"
    cd $WEBICS_HOME
fi
export NODE_ENV=development

#exec node ./scans/backend/nodejs/server.js -l logs/node.out -e logs/node.err
exec node ./scans/backend/nodejs/server.js

