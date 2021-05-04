""" 
 
 RPi Configuration

 !!!
 Stream and video size must be multiple of 16 in x-direction and multiple of 32 in y-direction!
 !!!
 
"""

PORT             = 5000
RECORDING_FOLDER = '../recordings'
CAMERA_SETTINGS  = 'camera_settings.json'
STREAM_SIZE      = (960, 544)
#VIDEO_SIZE       = (1920, 1088)
VIDEO_SIZE       = (1920, 1080)
MOTION_THRESHOLD = 120
CAMERA_MODULE    = "cvcamera" # or cvcamera
