#! /bin/sh

function KillPidFromTcpPort() {
    process=$(lsof -iTCP:$1 -sTCP:LISTEN | grep LISTEN)
    pname=$(echo $process| awk '{print $1}')
    pid=$(echo $process| awk '{print $2}')

    if test "x$pid" == "x"; then
        echo "No process is listening on TCP:$1."
        return
    fi

    echo "Process $pid($pname) is listening on TCP:$1, kill it."
    kill -SIGTERM $pid
}

function CheckPortUp() {
    while [[ 0 ]]
    do
        echo "Waiting for port $1 to be up."
        process=$(lsof -iTCP:$1 -sTCP:LISTEN | grep LISTEN)
        if test "x$process" != "x"; then
            echo "TCP:$1 is up."
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

mongodb_port=27017
gateway_port=80
