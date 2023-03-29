""" 
 
 RPi Configuration
 
"""

PORT               = 5000
RECORDING_FOLDER   = '../recordings'

VERSION            = '1.0'

# Camera configuration

#CAMERA_SIZE          = (640, 480)
#CAMERA_SIZE          = (1920, 1080)
CAMERA_SIZE          = (1640, 1232)
#CAMERA_SIZE          = (3280, 2464)
CAMERA_SENSOR_MODE   = 4 # 0 for 3280x2464
#CAMERA_REC_FPS       = 25
CAMERA_SETTINGS      = 'camera_settings.json'

STREAM_SIZE         = (640, 400)
#STREAM_SIZE          = (1280, 720)

CAMERA_MODULE       = "rpicamera" # or cvcamera

# Sensor configuration

PMSENSOR_DEVICE     = "/dev/ttyAMA0"
PMSENSOR_INTERVAL   = 2.0

PMSENSOR_MODULE     = "sps30"
