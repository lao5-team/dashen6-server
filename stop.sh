#! /bin/sh

. ./common.sh

CheckSid
KillPidFromTcpPort $gateway_port
KillPidFromTcpPort $mongodb_port
