#! /bin/sh

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

mongodb_port=27017
gateway_port=80
