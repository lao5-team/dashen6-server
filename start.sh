#! /bin/sh

. ./common.sh

CheckSid

echo "starting mongodb"
mongod --dbpath=./mongodb --port $mongodb_port >> mongodb.log 2>&1 &
CheckPortUp $mongodb_port

echo "starting gateway"
python gateway.py $gateway_port >> gateway.log 2>&1 &
CheckPortUp $gateway_port
