#!/bin/sh

echo "Install and start systemd service ..."
sudo install camadmin.service /etc/systemd/system
sudo systemctl enable camadmin
sudo systemctl start camadmin
