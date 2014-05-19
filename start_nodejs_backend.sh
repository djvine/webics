export WEBICS_HOME=/local/webics
export NODE_ENV=production

chdir $WEBICS_HOME
exec node scans/backend/nodejs/server.js -l logs/node.out -e logs/node.err

