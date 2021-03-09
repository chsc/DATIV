from threading import Thread
import picamera
import cv2

# https://picamera.readthedocs.io/en/release-1.10/index.html

class RPiVideoCamera:
    def __init__(self):
        self.frame = None
        self.running = False
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

if __name__ == "__main__":
    vid = RPiVideoCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
