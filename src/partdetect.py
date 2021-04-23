import cv2
import numpy
import detector

class ParticleDetector(detector.Detector):
    def detect(self, image):
        grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #kernel = numpy.ones((1, 1), numpy.uint8)
        #dilation = cv2.dilate(grayimg, kernel, iterations = 1)
        ret, thresh = cv2.threshold(grayimg, 127, 255, cv2.THRESH_BINARY)
        img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        #print(contours)
        #print(hierarchy)
        #contimage = cv2.drawContours(image, contours, -1, (0,255,0), 1)
        #cv2.imshow('cimage', contimage)

        particles = []
        for cnt in contours:
            #print(cnt)
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            M = cv2.moments(cnt)
            m00 = M['m00']
            if m00 != 0:
                cx = M['m10'] / m00
                cy = M['m01'] / m00
                particles.append((cx, cy, area))
        return particles

if __name__ == "__main__":
    img = cv2.imread('../data/test.png', cv2.IMREAD_COLOR)
    cv2.imshow('image',img)
    pd = ParticleDetector()
    particles = pd.detect(img)
    print(particles)
    print([detector.pixel_to_µm(p, 0.5, 0.5) for p in particles])
    cv2.waitKey(0)
