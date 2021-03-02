import cv2

class CVVideoRecorder:
    def __init__(self, filename, size, fps):
        #self.out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc('M','J','P','G'), fps, size)
        self.out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc('M','J','P','G'), 25, (1280, 720))

    def __del__(self):
        self.out.release()

    def write(self, frame):
        self.out.write(frame)

if __name__ == "__main__":
    vid = CVVideoRecorder('test', (1280, 720), 25)
