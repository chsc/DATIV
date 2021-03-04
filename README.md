# Portable RPI Microscope

## Web Interface

![WebInterface](/doc/web_interface.png)

## Install

You need to install the following software packages:

* **Python** 3.x
* **Flask**
* **OpenCV** for Python

Open the command line to install the required software packages:

    sudo apt-get install python3
    sudo apt-get install python3-flask
    sudo apt-get install python3-opencv

Clone the repository:

    git clone https://gitlab.hzdr.de/hzdri/ext/rpimicro.git

Change to the source directory and start the server with:

    python3 rpimicro.py

Open your browser and enter the following URL:

    http://<rpi-ip-address>:5000

## TODO

* Movement detection
* Build-in particle/object detection

## Notes

[Additional notes...](doc/NOTES.md)
