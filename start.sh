#! /bin/sh
#
# author: yafei
# start services

. ./common.sh

CheckSid

yes=$(CheckPort $mongodb_port)
if test $yes == "1"; then
    echo "Port $mongodb_port is occupied now."
    exit 1
fi

yes=$(CheckPort $gateway_port)
if test $yes == "1"; then
    echo "Port $gateway_port is occupied now."
    exit 1
fi

yes=$(CheckPort $photo_port)
if test $yes == "1"; then
    echo "Port $photo_port is occupied now."
    exit 1
fi

echo "Starting mongodb..."
mongod --dbpath=./mongodb --port $mongodb_port >> mongodb.log 2>&1 &
CheckPortUp $mongodb_port

echo "Starting gateway..."
python py/gateway.py $gateway_port >> gateway.log 2>&1 &
CheckPortUp $gateway_port
#
echo "Starting photo..."
python py/photo.py $photo_port >> photo.log 2>&1 &
CheckPortUp $photo_port
