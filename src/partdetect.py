import cv2
import numpy
import detector
import camera


class ParticleDetectorThreshold(detector.Detector):
    def __init__(self):
        self.timage = True
        self.threshold = 40
        self.maxArea = 200
        self.minArea = 3
    
    def set_threshold(self, th):
        self.threshold = th

    def get_threshold(self):
        return self.threshold    
    
    def detect(self, image, psx, psy, genout):
        #grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        flag = cv2.THRESH_BINARY
        if self.threshold == -1:
            flag += cv2.THRESH_OTSU
        elif self.threshold == -2:
            flag += cv2.THRESH_TRIANGLE
        ret, thresh = cv2.threshold(image, self.threshold, 255, flag)
        
        ret = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = ret[0]
        if len(ret) == 3: # for old version of find contours (pre 3.2)
            contours = ret[1]
        
        contimage = None
        if genout:
            contimage = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                
        particles = []
        for i in range(len(contours)):
            cnt = contours[i]
            
            area = cv2.contourArea(cnt)
            if area > self.maxArea or area < self.minArea:
                cv2.drawContours(contimage, contours, i, (0, 128, 255), 1)
                continue
                
            cx, cy = detector.contour_center(cnt)
            if not camera.in_passe_partout(image, (cx, cy), psx, psy):
                cv2.drawContours(contimage, contours, i, (0, 0, 255), 1)
                continue
            
            if genout:
                cv2.drawContours(contimage, contours, i, (0, 255, 0), 1)
                
            bx, by, bw, bh = cv2.boundingRect(cnt)
            
            particles.append((bx, by, bw, bh, cx, cy, area))
            
        return contimage, particles
        
class ParticleDetectorDifference(detector.Detector):
    def __init__(self, ratio = 1.1):
        #self.bsub = cv2.createBackgroundSubtractorKNN(2, 40, False)
        self.bsub = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        self.threshold = 230
        self.maxArea = 200
        self.minArea = 4
    
    def set_threshold(self, th):
        self.threshold = th
        if th >= 0:
            self.bsub.setVarThreshold(th)

    def get_threshold(self):
        return self.threshold    
    
    def detect(self, image, psx, psy, genout):
        #return image, []
        #grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fbmask = self.bsub.apply(image)
        
        ret = cv2.findContours(fbmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = ret[0]
        if len(ret) == 3: # for old version of find contours (pre 3.2)
            contours = ret[1]
        
        particles = []
        contimage = None
        if genout:
            contimage = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        for i in range(len(contours)):
            cnt = contours[i]
            
            area = cv2.contourArea(cnt)
            if area > self.maxArea or area < self.minArea:
                cv2.drawContours(contimage, contours, i, (0, 128, 255), 1)
                continue
            
            cx, cy = detector.contour_center(cnt)
            if not camera.in_passe_partout(image, (cx, cy), psx, psy):
                cv2.drawContours(contimage, contours, i, (0, 0, 255), 1)
                continue
                
            bx, by, bw, bh = cv2.boundingRect(cnt)
            
            particles.append((bx, by, bw, bh, cx, cy, area))
                
            if genout:
                cv2.drawContours(contimage, contours, i, (0, 255, 0), 1)
            
        return contimage, particles


        
        
        
        
        
        
        
        
        
       
        #if self.camera.motiondet.detect_motion(ydata):
            #print("###")
        #    r, th = cv2.threshold(ydata, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        #    cv2.imwrite(str(self.cnt) + "img.png", th)
        
            #cv2.imwrite(str(self.cnt) + "img.png", self.camera.motiondet.delta)
        
        #mask = self.backsub.apply(ydata)
        #mask = mask[mask > 200]
        
        #height, width = mask.shape
        #avg = cv2.sumElems(mask)[0] / (width * height) * 100.0
        #if avg > 10:
        #     print(avg)
        #     cv2.imwrite(str(self.cnt) + "img.png", mask)
        
class ParticleDetector3(detector.Detector):
    def __init__(self, ratio = 1.1):
        self.reject_ratio = ratio
        self.threshold = 127

    def set_threshold(self, th):
        self.threshold = th

    def get_threshold(self):
        return self.threshold

    def detect(self, image, genout):
        grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #kernel = numpy.ones((1, 1), numpy.uint8)
        #dilation = cv2.dilate(grayimg, kernel, iterations = 1)
        flag = cv2.THRESH_BINARY_INV
        if self.threshold == -1:
            flag += cv2.THRESH_OTSU
        elif self.threshold == -2:
            flag += cv2.THRESH_TRIANGLE
        ret, thresh = cv2.threshold(grayimg, self.threshold, 255, flag)
        #cv2.imshow('thresh', thresh)
        #cv2.waitKey(0)
        #img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ret = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = ret[0]
        if len(ret) == 3: # for old version of find contours (pre 3.2)
            contours = ret[1]
 
        idx = 0
        particles = []
        contimage = None
        if genout:
            contimage = image
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            U = detector.equi_perimeter(area)
            perimeter = cv2.arcLength(cnt, True)
            is_round = False;
            if U != 0:
                ratio = perimeter / U
                is_round = ratio < self.reject_ratio
                ##print(dd)
            if is_round:
                M = cv2.moments(cnt)
                m00 = M['m00']
                if m00 != 0:
                    cx = M['m10'] / m00
                    cy = M['m01'] / m00
                    d = detector.equi_diameter(area) / 2
                    particles.append((cx, cy, area))
                    if genout:
                        cv2.drawContours(contimage, contours, i, (255,255,255), 1)
                        #cv2.circle(contimage, (int(cx), int(cy)), int(d), (255,255,0), 1)
                        cv2.putText(image, str(idx), (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
                        idx += 1
            else:
                if genout:
                    cv2.drawContours(contimage, contours, i, (0,0,255), 1)

        return contimage, particles


class ParticleDetector2(detector.Detector):
    def __init__(self, ratio = 1.1):
        self.reject_ratio = ratio
        self.threshold = 127

    def set_threshold(self, th):
        self.threshold = th

    def get_threshold(self):
        return self.threshold

    def detect(self, image, genout):
        grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        particles = []
        #cv2.imshow('image', image)
        #edges = cv2.Canny(image, 100, 200)
        ret, thresh = cv2.threshold(grayimg, 120, 255, cv2.THRESH_BINARY_INV)
        ret, thresh2 = cv2.threshold(grayimg, 180, 255, cv2.THRESH_BINARY)
        th = thresh + thresh2
        cv2.imshow('edges', th)
        return thresh, particles

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
        
if __name__ == "__main__":
    dir = "/home/christoph/Dokumente/bilder/"
    #img = cv2.imread('../data/test.png', cv2.IMREAD_COLOR)
    #img = cv2.imread(dir + "Image_2021-04-23_23-57-45_126441.png", cv2.IMREAD_COLOR)
    #cv2.imshow('img',img)
    pd = ParticleDetector2()
    #detector.detect_image(pd, '../data/test_cam_02.png', '../data/detect_test_cam_02.png', "../data/test_cam_02.csv", 1.5, 1.5)
    detector.detect_image(pd, dir + "Image_2021-04-23_23-57-45_126441.png", dir + "Image_2021-04-23_23-57-45_126441_det.png", dir + "det.csv", 15, 15)
    #img, particles = pd.detect(img)
    #cv2.imshow('contimage', image)
    #print(particles)
    #print([detector.pixel_to_µm(p, 0.5, 0.5) for p in particles])
    cv2.waitKey(0)
