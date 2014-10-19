#! /bin/sh
#
# author: yafei
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
curl -v ${url}/login 1>stdout 2>stderr
r=$(cat stderr | grep " 401")
CheckNotEmpty "$r" "login 1"


curl -v ${url}/login?user=kimi -D cookie 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "login 2"


curl -v ${url}/login -b cookie 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "login 3"
r=$(cat stdout | grep "Already login")
CheckNotEmpty "$r" "login 3"


# newid saveid loadid
id=$(curl -v ${url}/newid -b cookie 2>stderr | python ./json_helper.py id)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "newid"
CheckNotEmpty "$id" "newid"


echo -e "$id\r\n[123]\r\n" > data
curl -v ${url}/saveid -b cookie --data-binary @data 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "saveid"


data=$(curl -v ${url}/loadid?id=$id -b cookie 2>stderr | python ./json_helper.py data)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "loadid"
CheckEqual "$data" "[123]" "loadid"


# db
id=$(curl -v "${url}/db?action=new&table=ut" -b cookie -d dummy 2>stderr | python ./json_helper.py id)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db new"
CheckNotEmpty "$id" "db new"


curl -v "${url}/db?action=set&table=ut&id=$id" -b cookie -d 123 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db set"


data=$(curl -v "${url}/db?action=get&table=ut&id=$id" -b cookie -d dummy 2>stderr | python ./json_helper.py data)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db get"
CheckEqual "$data" "123" "db get"


id2=$(curl -v "${url}/db?action=set&table=ut" -b cookie -d 456 2>stderr | python ./json_helper.py id)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db set 2"


data=$(curl -v "${url}/db?action=get&table=ut&id=$id2" -b cookie -d dummy 2>stderr | python ./json_helper.py data)
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db get 2"
CheckEqual "$data" "456" "db get 2"


curl -v "${url}/db?action=del&table=ut&id=$id" -b cookie -d dummy 1>stdout 2>stderr
r=$(cat stderr | grep " 200 OK")
CheckNotEmpty "$r" "db del"


curl -v "${url}/db?action=get&table=ut&id=$id" -b cookie -d dummy 1>stdout 2>stderr
r=$(cat stderr | grep " 500 Internal Server Error")
CheckNotEmpty "$r" "db get 3"
r=$(cat stdout | grep "Couldn't load id")
CheckNotEmpty "$r" "db get 3"


rm -f cookie data stdout stderr
