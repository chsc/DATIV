
import os
import json
import cv2
import numpy as np
from enum import Enum

class Mode(Enum):
    RECORD_OFF    = 0
    RECORD_MANUAL = 1
    RECORD_MOTION = 2

def draw_passe_partout(image, orig_size, ruler_length, ruler_xres, psx, psy):
    sy, sx = image.shape[:2]
    #print(sx, sy)
    vx = orig_size[0]
    px = sx / 2 * (psx / 100.0)
    py = sy / 2 * (psy / 100.0)
    pts = np.array([[px, py], [sx - px, py], [sx - px, sy - py], [px, sy - py]], np.int32)
    pts = pts.reshape((-1, 1, 2))
    image = cv2.polylines(image, [pts], True, (0, 0, 128), 1)
    xscale = sx / vx
    ruler_len = int(ruler_length / ruler_xres * xscale)
    image = cv2.line(image, (10, sy - 10), (10 + ruler_len, sy - 10), (0, 255, 0), 1)
    image = cv2.line(image, (10, sy - 11), (10, sy - 9), (0, 255, 0), 1)
    image = cv2.line(image, (10 + ruler_len, sy - 11), (10 + ruler_len, sy - 9), (0, 255, 0), 1)
    return image

def get_camera_parameters(data, camera):
    data['iso'] = camera.get_iso()
    data['brightness'] = camera.get_brightness()
    data['contrast'] = camera.get_contrast()
    data['ruler_length'] = camera.get_ruler_length()
    data['ruler_xres'] = camera.get_ruler_xres()
    data['ruler_yres'] = camera.get_ruler_yres()
    data['passe_partout_h'] = camera.get_passe_partout_h()
    data['passe_partout_v'] = camera.get_passe_partout_v()

def set_camera_parameters(data, camera):
    camera.set_iso(data['iso'])
    camera.set_brightness(data['brightness'])
    camera.set_contrast(data['contrast'])
    camera.set_ruler_length(data['ruler_length'])
    camera.set_ruler_xres(data['ruler_xres'])
    camera.set_ruler_yres(data['ruler_yres'])
    camera.set_passe_partout_h(data['passe_partout_h'])
    camera.set_passe_partout_v(data['passe_partout_v'])

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
    
    def save_state(self, filename):
        data = {}
        get_camera_parameters(data, self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent = 4)

    def load_state(self, filename):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            data = json.load(f)
            set_camera_parameters(data, self)

