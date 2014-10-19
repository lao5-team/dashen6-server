#! /bin/sh
#
# author: yafei
# stop services

. ./common.sh

CheckSid
KillPidFromTcpPort $photo_port
KillPidFromTcpPort $gateway_port
KillPidFromTcpPort $mongodb_port
