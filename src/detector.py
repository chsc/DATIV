
import numpy

def equi_diameter(area):
	return numpy.sqrt(4 * area / numpy.pi)

def pixel_to_µm(t, sx, sy):
	(cx, cy, area) = t
	area_µm = area * sx * sy
	return (cx * sx, cy * sy, area_µm, equi_diameter(area_µm))

class Detector:
    def detect(self, image):
        pass
