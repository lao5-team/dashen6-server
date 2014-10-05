#! /bin/sh

. ./common.sh

CheckSid

echo "starting mongodb"
mongod --dbpath=./mongodb --port 27017 > mongodb.log 2>&1 &
CheckPortUp 27017

echo "starting gateway"
python gateway.py 80 > gateway.log 2>&1 &
CheckPortUp 80
