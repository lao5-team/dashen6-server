#! /bin/sh

. ./common.sh

CheckSid
KillPidFromTcpPort 80
KillPidFromTcpPort 27017
