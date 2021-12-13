import cv2
import numpy

class MotionDetector:
    def __init__(self, threshold):
        self.threshold = threshold
        self.prev_frame = None
        self.delta = None

    def detect_motion(self, image):
        if self.prev_frame is None:
            self.prev_frame = image
            #self.prev_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #self.prev_frame = cv2.GaussianBlur(self.prev_frame, (21, 21), 0)
            #self.prev_frame = cv2.medianBlur(self.prev_frame, 5)
            return False
        #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)
        #gray = cv2.medianBlur(gray, 5)
        
        self.delta = cv2.absdiff(self.prev_frame, image)
        #height, width = delta.shape
        #avg_delta = cv2.sumElems(delta)[0] / (width * height * 255) * 100.0
        
        self.prev_frame = image

        amax = numpy.amax(self.delta) / 2.55
        #print(amax)
        #print(avg_delta)
        
        return amax >= self.threshold
