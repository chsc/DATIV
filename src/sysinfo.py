import shutil
import socket
import subprocess
import shlex

def get_temperature():
    with open( "/sys/class/thermal/thermal_zone0/temp", "r" ) as input:
        temperature = float(input.readline()) / 1000.0
    return temperature
    
def get_temperature_bpi():
    with open( "/sys/class/thermal/thermal_zone0/temp", "r" ) as input:
        temperature = float(input.readline())
    return temperature

def get_disk_free():
    total, used, free = shutil.disk_usage("/")
    return int(total / 2**20), int(used / 2**20), int(free / 2**20)

def get_hostname():
    return socket.gethostname()

#def get_ip(adapter):
#    # returns the first ip address of
#    return netifaces.ifaddresses(adapter)[netifaces.AF_INET][0]['addr']

def set_time(time):
    return subprocess.call(shlex.split('sudo date -s "%s"' % time)) == 0


if __name__ == "__main__":
    print(get_hostname())
    print(get_temperature())
    print(get_disk_free())
