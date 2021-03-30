import cv2
import time
from threading import Thread
from threading import Lock
from motiondetect import MotionDetector

fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
#fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

class CVVideoCamera:
    def __init__(self, motiondet, size, thumbsize):
        self.lock = Lock()
        self.thread = None
        self.running = False
        # Motion detector
        self.motiondet = motiondet
        # Parameters
        self.iso = 100
        self.brightness = 50
        self.contrast = 0
        self.ruler_length = 200
        self.ruler_xres = 5
        self.ruler_yres = 5
        self.passe_partout_x = 25
        self.passe_partout_y = 25
        # OpenCV Camera
        self.recorder = None
        self.capture = cv2.VideoCapture(0)
        print('default camera resolution:', self.size())
        if type(size) == tuple:
            print('new camera resolution:', size)
            #self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
            #self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1]) # 720p
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 720p
            print('new camera resolution:', self.size())
        ret, self.frame = self.capture.read()

    def __del__(self):
        self.capture.release()
        if self.recorder:
            self.recorder.release()

    def size(self):
        return (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def fps(self):
        return self.capture.get(cv2.CAP_PROP_FPS)

    def read(self):
        ret, frame = self.capture.read()
        return frame

    def camera_thread(self, callback):
        while self.running:
            #print("frame:")
            ret = False
            #with self.lock:
            ret, self.frame = self.capture.read()
            if ret and callback is not None:
                callback(self.frame)
                
    def run(self, callback):
        self.running = True
        self.thread = Thread(target=self.camera_thread, args=(callback,))
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def frame_callback(self, frame):
        if self.recorder is not None:
            print("recording frame")
            self.recorder.write(frame)

    def playback(self):
        self.stop()
        self.run(self.frame_callback)

    def record(self, filename):
        global fourcc
        self.recorder = cv2.VideoWriter(filename, fourcc, self.fps(), self.size())

    def stop_recording(self):
        if self.recorder is not None:
            self.recorder = None

    def record_motion_callback(frame):
        is_moving = motion_detector.detect_motion(frame)
        if is_moving:
            print("movement detected")
            global fourcc
            self.recorder = cv2.VideoWriter(filename, fourcc, self.fps(), self.size())

        if video_recorder is not None:
            print("recording frame")
            video_recorder.write(frame)

    def record_motion(self, filenamegen):
        self.stop()
        self.run(self.record_motion_callback)

    def capture_still_image(self, filename):
        with self.lock:
            if self.frame is not None:
                cv2.imwrite(filename, self.frame);


    def set_iso(self, iso):
        print("ISO not supported", iso)
        self.iso = iso

    def get_iso(self):
        print("ISO not supported", self.iso)
        return self.iso

    def set_brightness(self, bright):
        print("Brightness not supported", bright)
        self.brightness = bright
    
    def get_brightness(self):
        print("Brightness not supported", self.brightness)
        return self.brightness

    def set_contrast(self, contrast):
        print("Contrast not supported", contrast)
        self.contrast = contrast

    def get_contrast(self):
        print("Contrast not supported", self.contrast)
        return self.contrast

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

    def set_passe_partout_x(self, px):
        self.passe_partout_x = px

    def get_passe_partout_x(self):
        return self.passe_partout_x

    def set_passe_partout_y(self, py):
        self.passe_partout_y = py

    def get_passe_partout_y(self):
        return self.passe_partout_y


if __name__ == "__main__":
    vid = CVVideoCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
