#!/bin/sh

echo "Install and start systemd service ..."
sudo install rpimicro.service /etc/systemd/system
sudo systemctl enable rpimicro
sudo systemctl start rpimicro
