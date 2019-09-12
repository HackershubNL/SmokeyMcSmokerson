apt-get update

apt-get -y dist-upgrade

apt-get -y install build-essential python3-dev python3-smbus git openjdk-8-jdk python3-pip

pip3 install -r requirements.txt

git clone https://github.com/blynkkk/lib-python.git python-blynk

cd python-blynk

pip3 install -e .

cd ..

mkdir /opt/blynkserver

wget "https://github.com/blynkkk/blynk-server/releases/download/v0.41.10/server-0.41.10-java8.jar" -P /opt/blynkserver

mkdir /opt/blynkserver/data

mkdir /var/log/blynkserver

cp blynk_server /etc/init.d

cp blynk_server.properties /opt/blynkserver

chmod 755 /etc/init.d/blynk_server

update-rc.d blynk_server defaults

/etc/init.d/blynk_server start

echo "Default credentials to log into the local Blynk server are: admin@smokey.test : admin . To change this log into the web UI on port 9443"

