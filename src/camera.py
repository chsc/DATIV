
from enum import Enum

class Mode(Enum):
    RECORD_OFF    = 0
    RECORD_MANUAL = 1
    RECORD_MOTION = 2

class CameraEvents:
    def video_start_recording(self, camera):
        return ''

    def video_end_recording(self, camera):
        None

    def image_start_capture(self, camera):
        return ''

    def image_end_recording(self, camera):
        None

class Camera:
    None
