"""
   Copyright 2022-2023 by Christoph Schunk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

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

PMSENSOR_SETTINGS   = 'pmsensor_settings.json'

PMSENSOR_DEVICE     = "/dev/serial0"
PMSENSOR_DEVICE_BPI = "/dev/ttyS3"
PMSENSOR_INTERVAL   = 2.0

PMSENSOR_MODULE     = "sps30"
