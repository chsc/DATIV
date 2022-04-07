# Portable RPI Microscope

## Web Interface

![WebInterface](/doc/web_interface.png)

## Quick Install

Clone the repository to `/home/pi`:

    git clone https://gitlab.hzdr.de/hzdri/ext/rpimicro.git

Change to the `rpimicro` directory and run `setup.sh` (**Make shure to enable the camera interface before runnig the script!**)!

## Standard Install

Before you begin, please make shure your system is up-to-date.
Run

    sudo apt update
    sudo apt full-upgrade

to do this.

You also need to install the following additional software packages:

* **Python** 3.x
* **Flask** Web Framework
* **OpenCV** for Python
* **Pi Camera** Python Modules

Open the command line to install the required software packages:

    sudo apt-get install python3
    sudo apt-get install python3-pip
    sudo apt-get install python3-flask
    sudo apt-get install python3-opencv
    sudo apt-get install python3-picamera

    pip3 install -U flask-cors
    pip3 install -U netifaces

**Before you run the server, make shure you have enabled the camera.
You can use the `raspi-config` tool to do this (*see Interface Options*).**

Now, start and install the service using systemd (works only if repsitory is cloned to /home/pi/rpimicro):

    sudo install rpimicro/systemd/rpimicro.service /etc/systemd/system
    sudo systemctl enable rpimicro
    sudo systemctl start rpimicro

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
