#!/bin/sh

echo "Install and start systemd service ..."
sudo install rpipmsensor.service /etc/systemd/system
sudo systemctl enable rpipmsensor
sudo systemctl start rpipmsensor
