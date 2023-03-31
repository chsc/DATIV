import numpy as np
from camera import Camera, CameraEvents, Mode, passe_partout_size

class MCamera(Camera):
    def __init__(self, camevents, camera_size, stream_size, smode):
        print('Null camera')
        self.resolution = camera_size
        w, h = stream_size
        self.stream_image = np.zeros((h, w, 3), dtype = np.uint8)
    
    def close(self):
        pass
    
    def set_resolution_and_mode(self, res, mode):
        return False
    
    def capture_still_image(self):
        return False
        
    def record_video(self):
        return False
    
    def stop_recording(self):
        return False

    def capture_image_sequence(self):
        return False

    def stop_capture_image_sequence(self):
        return False
    
    def detect_objects(self, odet):
        return False

    def stop_detect_objects(self):
        return False


    def get_stream_image(self):
        return self.stream_image
        
    
    def is_recording(self):
        return False

    def get_resolution(self):
        return self.resolution
    
    def set_fps(self, fps):
        self.framerate = fps
        
    def get_fps(self):
        return float(self.framerate)
        
    def set_shutter_speed(self, shutter):
        self.shutter_speed = shutter
        
    def get_shutter_speed(self):
        return self.shutter_speed
        
    def set_iso(self, iso):
        self.iso = iso

    def get_iso(self):
        return self.iso

    def set_brightness(self, bright):
        self.brightness = bright

    def get_brightness(self):
        return self.brightness

    def set_contrast(self, contrast):
        self.contrast = contrast

    def get_contrast(self):
        return self.contrast
        
    def set_zoom(self, zoom):
        self.zoom = zoom
        
    def get_zoom(self):
        return self.zoom

    def set_ruler_xres(self, xres):
        self.ruler_xres = xres

    def get_ruler_xres(self):
        return self.ruler_xres

    def set_ruler_yres(self, yres):
        self.ruler_yres = yres

    def get_ruler_yres(self):
        return self.ruler_yres

    def set_ruler_length(self, length):
        self.ruler_length = length

    def get_ruler_length(self):
        return self.ruler_length

    def set_passe_partout_h(self, ph):
        self.passe_partout_h = ph

    def get_passe_partout_h(self):
        return self.passe_partout_h

    def set_passe_partout_v(self, pv):
        self.passe_partout_v = pv

    def get_passe_partout_v(self):
        return self.passe_partout_v

    def set_capture_interval(self, iv):
        self.capture_interval = iv
        
    def get_capture_interval(self):
        return self.capture_interval
