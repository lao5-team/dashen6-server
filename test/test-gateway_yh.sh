#! /bin/sh
#
# author: yh
# gateway functional tests

cd $(dirname $0)
. ../common.sh
port=8080
url="http://localhost:$port"
yes=$(CheckPort $port)
if test $yes != "1"; then
    echo "Port $port is not open."
    exit 1
fi


# login
curl -v ${url}/login?user=yihao -D cookie 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "login 2"


curl -v ${url}/login -b cookie 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "login 3"
r=$(cat stdout | grep "Already login")
CheckNotEmpty "$r" "login 3"


# db
user_data=$(curl -v "${url}/db?action=get_user&username=yihao" -b cookie -d dummy 2>stderr)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$user_data" "get_user"

data=$(curl -v "${url}/db?action=add_user_activity&field=doing&activity_id=activity0" -b cookie -d dummy 2>stderr | python ./json_helper.py data)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db add_user_activity"





rm -f cookie data stdout stderr
