from threading import Thread
import cv2

class CVVideoCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        print('size', self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # 720p
        self.running = False
        ret, self.frame = self.cap.read()

    def __del__(self):
        self.cap.release()

    def size(self):
        return (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

if __name__ == "__main__":
    vid = CVVideoCamera()
    while True:
        frame = vid.read()
        #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
        cv2.imshow('Camera - Press q for quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
