import cv2
import numpy as np
import datetime
import time
import picamera
from threading import Thread, Lock
from motiondetect import MotionDetector
from camera import Camera, CameraEvents, Mode

# https://picamera.readthedocs.io/en/release-1.10/index.html

class MCamera(Camera):
    def __init__(self, camevents, motiondet, camera_size, stream_size):
        self.frame = None
        self.running = False
        self.mode = Mode.RECORD_OFF
        # Events & Motion detector
        self.camevents = camevents
        self.motiondet = motiondet
        # sizes
        self.stream_size = stream_size
        self.stream_image = None
        self.cached_image = False
        # Parameters
        self.ruler_length = 200
        self.ruler_xres = 5
        self.ruler_yres = 5
        self.passe_partout_h = 25
        self.passe_partout_v = 25
        # Pi Camera
        self.camera = picamera.PiCamera()
        print('default camera resolution:', self.camera_size())
        print('framerate:', self.fps())
        if type(camera_size) == tuple:
            print('new camera resolution:', camera_size)
            self.camera.resolution = camera_size
            print('new camera resolution:', self.camera_size())

    def __del__(self):
        self.camera.close()

    def camera_thread(self):
        while self.running:
            if self.mode != Mode.RECORD_OFF:
                self.camera.wait_recording(1)
                print('wait recording')
                
    def start(self):
        self.running = True
        t = Thread(target=self.camera_thread)
        t.daemon = True
        t.start()

    def stop(self):
        self.running = False
        
    def record_video_manual(self):
        if self.mode != Mode.RECORD_OFF:
            return
        self.cached_image = True
        filename = self.camevents.video_start_recording(self)
        self.camera.start_recording(filename, format='h264')
        self.mode = Mode.RECORD_MANUAL

    def record_video_motion(self):
        if self.mode != Mode.RECORD_OFF:
            return
        self.cached_image = True
        filename = self.camevents.video_start_recording(self)
        self.camera.start_recording(filename, format='h264')
        self.mode = Mode.RECORD_MOTION        

    def stop_recording(self):
        self.mode = Mode.RECORD_OFF
        self.camera.stop_recording()
        self.camevents.video_end_recording(self)
        self.cached_image = False

    def is_recording(self):
        return self.mode != Mode.RECORD_OFF

    def capture_still_image(self):
        if self.mode != Mode.RECORD_OFF:
            return
        self.cached_image = True
        time.sleep(1)
        filename = self.camevents.image_start_capture(self)
        self.camera.capture(filename);
        self.camevents.image_end_capture(self)
        time.sleep(1)
        self.cached_image = False

    def get_stream_image(self):
        if self.cached_image:
            return self.stream_image
        try:
            (w, h) = self.stream_size
            image = np.empty((w * h * 3,), dtype=np.uint8)
            self.camera.capture(image, 'bgr', resize=self.stream_size, use_video_port=True)
            self.stream_image = image.reshape((h, w, 3))
            return self.stream_image
        except picamera.PiCameraError:
            return self.stream_image

    def camera_size(self):
        return self.camera.resolution

    def fps(self):
        return self.camera.framerate
        
    def set_iso(self, iso):
        self.camera.iso = iso

    def get_iso(self):
        return self.camera.iso

    def set_brightness(self, bright):
        self.camera.brightness = bright
    
    def get_brightness(self):
        return self.camera.brightness

    def set_contrast(self, contrast):
        self.camera.contrast = contrast

    def get_contrast(self):
        return self.camera.contrast

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

if __name__ == "__main__":
    
    class CamEvents(CameraEvents):
        def video_start_recording(self, camera):
            return 'video.mp4'

        def video_end_recording(self, camera):
            print("written to video file...")

        def image_start_capture(self, camera):
            print("writing to image file...")
            return 'image.png'

        def image_end_capture(self, camera):
            print("... written to image file")
            
        
    cev = CamEvents()
    c = MCamera(cev, None, (1920, 1088), (960, 544))
    time.sleep(2)
    c.capture_still_image()
    img = c.get_stream_image()
    cv2.imshow('Camera - Press q for quit', img)
    c.record_video_manual()
    c.camera.wait_recording(4)
    c.stop_recording()
    #cv2.waitKey(-1)
    #c.camera.start_preview()
    #
    
    #while True:
    #    frame = vid.read()
    #    #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
    #    cv2.imshow('Camera - Press q for quit', frame)
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #       break
