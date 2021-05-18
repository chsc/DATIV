import shutil
import socket

def get_temperature():
    with open( "/sys/class/thermal/thermal_zone0/temp", "r" ) as input:
        temperature = float( input.readline() ) / 1000.0
    return temperature

def get_disk_free():
    total, used, free = shutil.disk_usage("/")
    return int(total / 2**20), int(used / 2**20), int(free / 2**20)

def get_hostname():
    return socket.gethostname()