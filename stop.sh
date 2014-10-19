#! /bin/sh
#
# author: yafei
# stop services

. ./common.sh

CheckSid
KillPidFromTcpPort $gateway_port
KillPidFromTcpPort $mongodb_port
KillPidFromTcpPort $photo_port
