#!/bin/sh
rm -f *.tar.gz

tar --exclude='./.gitignore' --exclude='./.git' --exclude='./recordings' --exclude='./firmware_rpimicro.tar.gz' -pzcvf firmware_rpimicro.tar.gz .
