#!/bin/sh
rm -f *.tar.gz
#zip -r firmware_picam.zip . -x recordings/**
tar --exclude  .git recordings firmware_rpimicro.tar.gz -pzcvf firmware_rpimicro.tar.gz .
