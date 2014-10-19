#! /bin/sh
#
# author: yafei
# common functions and variables for shell utilities

mongodb_port=27017
gateway_port=80
photo_port=81

function KillPidFromTcpPort() {
    process=$(lsof -iTCP:$1 -sTCP:LISTEN | grep LISTEN)
    if test "x$process" == "x"; then
        echo "No process is listening on TCP:$1."
        return
    fi
    pname=$(echo $process| awk '{print $1}')
    pid=$(echo $process| awk '{print $2}')

    echo "Process $pid($pname) is listening on TCP:$1."
    echo "Killing it..."
    kill -15 $pid
    echo "Done."
}

function CheckPort() {
    process=$(lsof -iTCP:$1 -sTCP:LISTEN | grep LISTEN)
    if test "x$process" != "x"; then
        echo "1"
    else
        echo "0"
    fi
}

function CheckPortUp() {
    while [[ 0 ]]
    do
        echo "Waiting for port $1 to be up."
        process=$(lsof -iTCP:$1 -sTCP:LISTEN | grep LISTEN)
        if test "x$process" != "x"; then
            echo "TCP:$1 is up."
            echo "Done."
            return
        fi
        sleep 1
    done
}

function CheckSid() {
    user=$(whoami)
    if test $user != "root"; then
        echo 'Please execute this scripts with "sudo".'
        exit 1
    fi
}

function CheckNotEmpty() {
    if test "x$1" == "x"; then
        echo "[$2] Result should not be empty."
    else
        echo "Pass."
    fi
}

function CheckEqual() {
    if test $1 != $2; then
        echo "[$3] Result should equal: $1 vs $2."
    else
        echo "Pass."
    fi
}
