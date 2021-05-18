import cv2
import datetime
from threading import Thread, Lock
from motiondetect import MotionDetector
from camera import Camera, Mode

fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
#fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

class MCamera(Camera):
    def __init__(self, camevents, motiondet, camera_size, stream_size):
        self.lock = Lock()
        self.thread = None
        self.running = False
        self.mode = Mode.RECORD_OFF
        # Events & Motion detector
        self.camevents = camevents
        self.motiondet = motiondet
        # sizes
        self.stream_size = stream_size
        # Parameters
        self.iso = 100
        self.brightness = 50.0
        self.contrast = 0.0
        self.ruler_length = 200.0
        self.ruler_xres = 5.0
        self.ruler_yres = 5.0
        self.passe_partout_h = 25
        self.passe_partout_v = 25
        # OpenCV Camera
        self.recorder = None
        self.capture = cv2.VideoCapture(0)
        print('default camera resolution:', self.camera_size())
        if type(camera_size) == tuple:
            print('new camera resolution:', camera_size)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, camera_size[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_size[1])
            print('new camera resolution:', self.camera_size())
        ret, self.frame = self.capture.read()

    def __del__(self):
        self.capture.release()
        if self.recorder:
            self.recorder.release()

    def camera_size(self):
        return (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def fps(self):
        return self.capture.get(cv2.CAP_PROP_FPS)

    def camera_thread(self):
        global fourcc
        while self.running:
            ret = False
            ret, self.frame = self.capture.read()
            if not ret:
                continue
            if self.mode == Mode.RECORD_MANUAL:
                if self.recorder is None:
                    filename = self.camevents.video_start_recording(self)
                    self.recorder = cv2.VideoWriter(filename, fourcc, self.fps(), self.camera_size())
                if self.recorder is not None:
                    print("manual recording frame")
                    self.recorder.write(self.frame)
            elif self.mode == Mode.RECORD_MOTION:
                is_moving = self.motiondet.detect_motion(self.frame)
                if is_moving:
                    print("movement detected")
                    self.lastmotiontime = datetime.datetime.now()
                    if self.recorder is None:
                        print("start recording")
                        filename = self.camevents.video_start_recording(self)
                        self.recorder = cv2.VideoWriter(filename, fourcc, self.fps(), self.camera_size())
                else:
                    if self.recorder is not None:
                        now = datetime.datetime.now()
                        if now > self.lastmotiontime + datetime.timedelta(seconds = 5):
                            print("no movement for 5 seconds.. closing stream")
                            self.recorder = None
                            self.camevents.video_end_recording(self)
                if self.recorder is not None:
                    print("movement recording frame")
                    self.recorder.write(self.frame)
            elif self.mode == Mode.RECORD_OFF:
                if self.recorder is not None:
                    self.recorder = None
                    self.camevents.video_end_recording(self)

    def start(self):
        self.running = True
        self.thread = Thread(target=self.camera_thread)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def record_video_manual(self):
        if self.mode != Mode.RECORD_OFF:
            return
        self.mode = Mode.RECORD_MANUAL
        while self.recorder is None:
            None

    def record_video_motion(self):
        if self.mode != Mode.RECORD_OFF:
            return
        self.mode = Mode.RECORD_MOTION
        while self.recorder is None:
            None

    def stop_recording(self):
        self.mode = Mode.RECORD_OFF
        # wait until closed...
        while self.recorder is not None:
            None

    def is_recording(self):
        return self.mode != Mode.RECORD_OFF

    def capture_still_image(self):
        with self.lock:
            if self.frame is not None:
                filename = self.camevents.image_start_capture(self)
                cv2.imwrite(filename, self.frame);
                self.camevents.image_end_capture(self)

    def get_stream_image(self):
        with self.lock:
            if self.frame is None:
                return None
            return cv2.resize(self.frame, self.stream_size, interpolation=cv2.INTER_AREA)


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

    def set_passe_partout_h(self, ph):
        self.passe_partout_h = ph

    def get_passe_partout_h(self):
        return self.passe_partout_h

    def set_passe_partout_v(self, pv):
        self.passe_partout_v = pv

    def get_passe_partout_v(self):
        return self.passe_partout_v


if __name__ == "__main__":
    vid = MCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
