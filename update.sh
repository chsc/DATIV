#!/bin/sh

# git clone pi@192.168.1.10:/home/pi/rpimicro

git remote add primarycamera pi@192.168.1.10:/home/pi/rpimicro

git pull primarycamera master

./systemd/restart.sh
