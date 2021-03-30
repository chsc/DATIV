
import os
import json
import cv2
import numpy as np

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

def save_camera_state(c, filename):
    data = {
        'iso': c.get_iso(),
        'brightness': c.get_brightness(),
        'contrast': c.get_contrast(),
        'ruler_length': c.get_ruler_length(),
        'ruler_xres': c.get_ruler_xres(),
        'ruler_yres': c.get_ruler_yres(),
        'passe_partout_x': c.get_passe_partout_x(),
        'passe_partout_y': c.get_passe_partout_y(),
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent = 4)

def load_camera_state(c, filename):
    if not os.path.exists(filename):
        return
    with open(filename, 'r') as f:
        data = json.load(f)
        c.set_iso(data['iso'])
        c.set_brightness(data['brightness']),
        c.set_contrast(data['contrast']),
        c.set_ruler_length(data['ruler_length']),
        c.set_ruler_xres(data['ruler_xres']),
        c.set_ruler_yres(data['ruler_yres']),
        c.set_passe_partout_x(data['passe_partout_x']),
        c.set_passe_partout_y(data['passe_partout_y']),