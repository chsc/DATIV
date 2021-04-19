# Portable RPI Microscope

## Web Interface

![WebInterface](/doc/web_interface.png)

## Install

Before you begin, please make shure your system is up-to-date.
Run

    sudo apt update
    sudo apt full-upgrade

to do this.

You also need to install the following additional software packages:

* **Python** 3.x
* **Flask**
* **OpenCV** for Python

Open the command line to install the required software packages:

    sudo apt-get install python3
    sudo apt-get install python3-flask
    sudo apt-get install python3-opencv

Clone the repository:

    git clone https://gitlab.hzdr.de/hzdri/ext/rpimicro.git

Before you run the server, make shure you have enabled the camera.
You can use the *raspi-config* tool to doo this (Interface Options).

Now, change to the source directory (src) and start the server with:

    python3 rpimicro.py

Open your browser and enter the following URL:

    http://<rpi-ip-address>:5000

or

    http://localhost:5000

if you are running it on the Pi.

## TODO

* Build-in particle/object detection

## Notes

[Additional notes...](doc/NOTES.md)

## API

The camera can be remote controlled with a set of [HTTP requests](doc/API.md).
