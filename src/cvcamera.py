from threading import Thread
import cv2

class CVVideoCamera:
    def __init__(self):
        self.iso = 100
        self.brightness = 50
        self.contrast = 0
        self.cap = cv2.VideoCapture(0)
        print('camera resolution:', self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 720p
        self.running = False
        ret, self.frame = self.cap.read()

    def __del__(self):
        self.cap.release()

    def size(self):
        return (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def read(self):
        ret, frame = self.cap.read()
        return frame

    def camera_thread(self, callback):
        while self.running:
            ret, self.frame = self.cap.read()
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


if __name__ == "__main__":
    vid = CVVideoCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
