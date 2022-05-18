#!/bin/sh
rm -fR src/
rm -fR doc/
rm -fR systemd/
rm -f *.sh
rm -f *.md

tar -zxvf firmware_upload.tar.gz
rm -f firmware_upload.tar.gz
