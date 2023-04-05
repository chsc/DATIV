# Network Config

## Enable Ethernet Emulation (Raspberry Pi Zero 2 only)

Enable the Ethernet over USB functionality.
Mount the boot partition of your SD card.

Add the following line to your `config.txt` file:

    dtoverlay=dwc2

Add the following modules to load to your `cmdline.txt`:

    modules-load=dwc2,g_ether

Additional information:
https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-gadget

## Enable SSH

To enable SSH by creating an empty `ssh` file in your boot partition.

    echo '' > ssh

## WLAN and WPA Configuration

Create a `wpa_supplicant.conf` file:

    country=DE
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={
    ssid="NETGEAR94-5G-1"
    psk="melodicviolet891"
    key_mgmt=WPA-PSK
    }

For the Pi Zero use `NETGEAR94` for the SSID!

## General IP Configuration

### Static IP Adresses

    sudo nano /etc/dhcpcd.conf

### Ethernet and WLAN IP addresses

    interface eth0
    static ip_address=192.168.1.10/16
    static routers=192.168.1.1
    static domain_name_servers=8.8.8.8

    interface wlan0
    static ip_address=192.168.2.10/16
    static routers=192.168.1.1
    static domain_name_servers=8.8.8.8

For Pi Zeros `usb0` for the ethernet emulation!

## Connect via SSH

    ssh -X pi@192.168.1.10

## Web

    http://192.168.1.10:5000

# Network of 10 Cameras

| Camera/Type    | Description            | WLAN IP      | LAN IP       |
| -------------- | ---------------------- | ------------ | ------------ |
| Router         | Netgear Nighthak X6    | 192.168.1.1  | 192.168.1.1  |
| Master         | PC                     | 192.168.1.2  | 192.168.2.2  |
| camera00       | RPi 4, v2 Camera       | 192.168.1.10 | 192.168.2.10 |
| camera01       | RPi 4, v2 Camera       | 192.168.1.11 | 192.168.2.11 |
| camera02       | RPi Zero, v2 Camera    | 192.168.1.12 | 192.168.2.12 |
| camera03       | RPi Zero, v2 Camera    | 192.168.1.13 | 192.168.2.13 |
| camera04       | RPi Zero, v2 Camera    | 192.168.1.14 | 192.168.2.14 |
| camera05       | RPi 3 Type A+          | 192.168.1.15 | 192.168.2.15 |
| camera06       | BPi M2 Zero            | 192.168.1.16 | 192.168.2.16 |
| camera07       | BPi M2 Zero            | 192.168.1.17 | 192.168.2.17 |
| camera08       | BPi M2 Zero            | 192.168.1.18 | 192.168.2.18 |
| camera09       | BPi M2 Zero            | 192.168.1.19 | 192.168.2.19 |
| camera10       | RPi 4 (von Tom)        | 192.168.1.20 | 192.168.2.20 |
