# deploy.sh
mkdir /home/ubuntu/ML_web_dereverb
cd /home/ubuntu/ML_web_dereverb

sudo apt-get install python3.8-venv
sudo python3.8 -m pip install pip==21.2.4

# git pull
git stash
git pull origin master --force

echo "source venv"
python3.8 -m venv venv
source venv/bin/activate
date >> date.log

pip install -r requirements.txt

echo "All done"