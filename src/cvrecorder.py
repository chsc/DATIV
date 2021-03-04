import cv2

class CVVideoRecorder:
    def __init__(self, filename, size, fps):
        print("---- size: ", size)
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        #fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        self.out = cv2.VideoWriter(filename, fourcc, fps, size)

    def __del__(self):
        self.out.release()

    def write(self, frame):
        self.out.write(frame)

if __name__ == "__main__":
    vid = CVVideoRecorder('test', (1280, 720), 25)
