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

import os
import json
import cv2
import enum
import numpy as np

class Mode(enum.Enum):
    RECORD_OFF    = 0
    VIDEO         = 1
    IMGSEQ        = 2
    OBJDET        = 3

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
    
def draw_particles_and_flowrate(image, volume, particles, pflow):
    sy, sx = image.shape[:2]
    image = cv2.putText(image, f"volume: {volume:.2f} cm^3  particles: {particles}  particle flow: {pflow:.2f} particles/s", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255,255,255), 1)
    return image

def in_passe_partout(image, p, psx, psy):
    sy, sx = image.shape[:2]
    x1 = sx / 2 * (psx / 100.0)
    y1 = sy / 2 * (psy / 100.0)
    x2 = sx - x1
    y2 = sy - y1
    return (x1 < p[0] < x2) and (y1 < p[1] < y2)
    
def passe_partout_size(res, psx, psy, ruler_xres, ruler_yres):
    sy, sx = res
    rx = sx * (100 - psx) / 100.0
    ry = sy * (100 - psy) / 100.0
    return rx * ruler_xres / 1000, ry * ruler_yres / 1000 # mm

def zoom_image(img, zoom):
    ih, iw, c = img.shape
    cx = iw / 2
    cy = ih / 2
    w = iw / (zoom / 100.0)
    h = ih / (zoom / 100.0)
    x = cx - w / 2
    y = cy - h / 2
    return img[int(y):int(y + h), int(x):int(x + w)]

def get_camera_parameters(data, camera):
    data['shutter_speed'] = camera.get_shutter_speed()
    data['iso'] = camera.get_iso()
    data['brightness'] = camera.get_brightness()
    data['contrast'] = camera.get_contrast()
    data['zoom'] = camera.get_zoom()
    data['ruler_length'] = camera.get_ruler_length()
    data['ruler_xres'] = camera.get_ruler_xres()
    data['ruler_yres'] = camera.get_ruler_yres()
    data['passe_partout_h'] = camera.get_passe_partout_h()
    data['passe_partout_v'] = camera.get_passe_partout_v()
    data['capture_interval'] = camera.get_capture_interval()

def set_camera_parameters(data, camera):
    camera.set_shutter_speed(data['shutter_speed'])
    camera.set_iso(data['iso'])
    camera.set_brightness(data['brightness'])
    camera.set_contrast(data['contrast'])
    camera.set_zoom(data['zoom'])
    camera.set_ruler_length(data['ruler_length'])
    camera.set_ruler_xres(data['ruler_xres'])
    camera.set_ruler_yres(data['ruler_yres'])
    camera.set_passe_partout_h(data['passe_partout_h'])
    camera.set_passe_partout_v(data['passe_partout_v'])
    camera.set_capture_interval(data['capture_interval'])
    

class CameraEvents:
    def video_start_recording(self, camera):
        return ''

    def video_end_recording(self, camera):
        pass

    def image_start_capture(self, camera):
        return ''

    def image_end_recording(self, camera):
        pass
        
    def objdet_start(self, camera):
        return''
        
    def objdet_end(self, camera):
        pass

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
            
def create_camera(modname, camevents, camera_size, stream_size, smode):
    module = __import__(modname)
    try:
        camera = module.MCamera(camevents, camera_size, stream_size, smode)
        return camera
    except Exception as e:
        print('Error initializing camera:', str(e))
        module = __import__('nullcamera')
        return module.MCamera(camevents, camera_size, stream_size, smode)
