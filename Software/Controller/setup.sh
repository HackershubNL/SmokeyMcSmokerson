sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus git

sudo pip install -r requirements.txt

git clone https://github.com/tdack/MAX6675.git

cd MAX6675

sudo python setup.py install