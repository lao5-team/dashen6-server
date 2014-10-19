#! /bin/sh


. ../common.sh
port=8080
url="http://localhost:$port"
yes=$(CheckPort $port)
if test $yes != "1"; then
    echo "Port $port is not open."
    exit 1
fi

set -e


echo -e "testfile\r\ntestdata\r\n" > data
curl -v ${url}/upload --data-binary @data 1>stdout 2>stderr
r=$(cat stderr | grep " 200")
CheckNotEmpty ${r} "upload"

url=$(cat stdout | python ./json_helper.py url)
data=$(curl $url 2>/dev/null)
CheckEqual $data "testdata" "upload"

rm -f data stdout stderr
