""" 
 
 RPi Configuration

 !!!
 Stream and video size must be multiple of 16 in x-direction and multiple of 32 in y-direction!
 !!!
 
"""

PORT               = 5000
RECORDING_FOLDER   = '../recordings'

CAMERA_SIZE        = (640, 480)
#CAMERA_SIZE        = (1920, 1080)
#CAMERA_SIZE        = (3280, 2464)

CAMERA_SENSOR_MODE = 7
CAMERA_FPS         = 25
CAMERA_SETTINGS    = 'camera_settings.json'
#STREAM_SIZE        = (960, 544)
STREAM_SIZE        = (640, 400)

MOTION_THRESHOLD   = 120
CAMERA_MODULE      = "rpicamera" # or cvcamera
