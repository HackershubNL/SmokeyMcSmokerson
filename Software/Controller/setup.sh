apt-get update
apt-get install build-essential python3-dev python3-smbus git openjdk-8-jdk

pip3 install -r requirements.txt

git clone https://github.com/blynkkk/lib-python.git python-blynk

cd python-blynk

pip3 install -e .

cd ..

mkdir /opt/blynkserver

wget "https://github.com/blynkkk/blynk-server/releases/download/v0.41.6/server-0.41.6-java8.jar" -O /opt/blynkserver

mkdir /opt/blynkserver/data

