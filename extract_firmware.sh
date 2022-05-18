#!/bin/sh
rm -fR src/
rm -fR doc/
rm -fR systemd/
rm -f *.sh
rm -f *.md
#unzip firmware.zip
tar -xf firmware_upload.tar.gz
