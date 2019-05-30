apt-get update

apt-get dist-upgrade

apt-get install build-essential python3-dev python3-smbus git openjdk-8-jdk python3-pip

pip3 install -r requirements.txt

git clone https://github.com/blynkkk/lib-python.git python-blynk

cd python-blynk

pip3 install -e .

cd ..

mkdir /opt/blynkserver

wget "https://github.com/blynkkk/blynk-server/releases/download/v0.41.6/server-0.41.6-java8.jar" -P /opt/blynkserver

mkdir /opt/blynkserver/data

cp blynk_server /etc/init.d

chmod 755 /etc/init.d/blynk_server

update-rc.d blynk_server defaults

/etc/init.d/blynk_server start

echo "Default credentials to log into the local Blynk server are: admin@blynk.cc : admin . To change this log into the web UI on port 9443"

