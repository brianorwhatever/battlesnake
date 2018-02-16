# Battlesnake

## Setup

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Setup ubuntu

```
sudo apt update
sudo apt install unzip -y
sudo apt -y autoremove
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt update
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo apt update
sudo apt install cuda -y

wget https://s3-us-west-2.amazonaws.com/battlesnake18/cudnn-9.1-linux-x64-v7.tgz
tar xf cudnn-9.1-linux-x64-v7.tgz
sudo cp cuda/include/*.* /usr/local/cuda/include/
sudo cp cuda/lib64/*.* /usr/local/cuda/lib64/

sudo apt install python-pip

export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```