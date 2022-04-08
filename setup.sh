#!/bin/sh

echo "Updating system ..."
sudo apt update
sudo apt full-upgrade

echo "Installing prerequisites ..."
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install python3-flask
sudo apt-get install python3-opencv
sudo apt-get install python3-picamera

pip3 install -U flask-cors
pip3 install -U netifaces

echo "Install and start systemd service ..."
sudo install systemd/rpimicro.service /etc/systemd/system
sudo systemctl enable rpimicro
sudo systemctl start rpimicro
