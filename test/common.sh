#! /bin/sh

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

