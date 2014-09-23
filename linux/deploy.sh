#! /bin/sh
#
# tested CentOS 6
#
set -e
set -x


sudo python --version
wget http://webpy.org/static/web.py-0.37.tar.gz
tar zxvf web.py-0.37.tar.gz
cd web.py-0.37
sudo python setup.py install
cd -
rm -rf web.py-0.37.tar.gz web.py-0.37

sudo cp mongodb.repo /etc/yum.repos.d/
sudo cp nginx.repo /etc/yum.repos.d/

sudo yum install -y mongodb-org
sudo yum install -y nginx

