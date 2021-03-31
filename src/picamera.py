from threading import Thread
import picamera
import cv2

# https://picamera.readthedocs.io/en/release-1.10/index.html

class RPiVideoCamera:
    def __init__(self):
        self.frame = None
        self.running = False
         # Parameters
        self.iso = 100
        self.brightness = 50
        self.contrast = 0
        self.ruler_length = 200
        self.ruler_xres = 5
        self.ruler_yres = 5
        self.passe_partout_x = 25
        self.passe_partout_y = 25
        
        self.camera = picamera.PiCamera()

    def __del__(self):
        camera.close()

    def size(self):
        return camera.resolution

    def fps(self):
        return camera.resolution

    def read(self):
        frame = None
        return frame

    def camera_thread(self, callback):
        while self.running:
            #ret, self.frame = self.cap.read()
            if ret and callback is not None:
                callback(self.frame)
                
    def run(self, callback):
        self.running = True
        t = Thread(target=self.camera_thread, args=(callback,))
        t.daemon = True
        t.start()

    def stop(self):
        self.running = False


    
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
    vid = RPiVideoCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
