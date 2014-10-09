#! /bin/sh

set -e

. ./common.sh
url="http://localhost:8080"


curl -v ${url}/login > result 2>&1
r=$(cat result | grep " 401")
CheckNotEmpty ${r} "login 1"


curl -v ${url}/login?user=kimi -D cookie > result 2>&1
r=$(cat result | grep " 200")
CheckNotEmpty ${r} "login 2"


curl -v ${url}/login -b cookie > result 2>&1
r1=$(cat result | grep " 200")
r2=$(cat result | grep "Already login")
CheckNotEmpty ${r1} "login 3"
CheckNotEmpty ${r2} "login 3"


curl -v ${url}/newid -b cookie > result 2>&1
r1=$(cat result | grep " 200")
r2=$(cat result | grep "id")
CheckNotEmpty ${r1} "newid"
CheckNotEmpty ${r2} "newid"


id=$(curl ${url}/newid -b cookie 2>/dev/null | python ./json_helper.py id)
echo -e "$id\r\n[123]\r\n" > data
curl -v ${url}/saveid -b cookie --data-binary @data > result 2>&1
r=$(cat result | grep " 200")
CheckNotEmpty ${r} "saveid"


data=$(curl ${url}/loadid?id=$id -b cookie 2>/dev/null | python ./json_helper.py data)
CheckEqual $data "[123]" "loadid"

rm -f cookie result data
