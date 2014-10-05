dashen6-server
=====================

部署環境
---------
在CentOS 6.3下測試通過.

python版本如果是2.6則需要先升級至2.7(最新版本即可,如2.7.8).

執行linux/deploy.sh

啟動
--------
> sudo ./start.sh

如果需要修改HTTP gateway的端口,修改common.sh中的:
> gateway_port=80

如果需要修改mongodb的端口,修改common.sh中的:
> mongodb_port=27017

和gateway_config.py中的:
> dbPort = 27017

停止
--------
> sudo ./stop.sh

數據庫備份
--------
目錄mongodb是數據庫文件,需要定期備份.

靜態文件
--------
目錄static是存放靜態文件的地方.

例如static目錄下有一個文件叫weijuhui.apk,我可以訪問下面的URL來下載該文件.

> http://117.78.3.87/static/weijuhui.apk

