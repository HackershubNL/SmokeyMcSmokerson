apt-get update
apt-get install build-essential python3-dev python3-smbus git

pip3 install -r requirements.txt

git clone https://github.com/blynkkk/lib-python.git python-blynk

cd python-blynk

pip3 install -e .

cd ..