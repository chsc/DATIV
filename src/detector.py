
import csv
import cv2
import numpy

def equi_diameter(area):
	return numpy.sqrt(4 * area / numpy.pi)

def equi_perimeter(area):
	return numpy.sqrt(4 * numpy.pi * area)

def pixel_to_µm(t, sx, sy):
	(cx, cy, area) = t
	area_µm = area * sx * sy
	return (cx * sx, cy * sy, area_µm, equi_diameter(area_µm))

class Detector:
    def detect(self, image, genout):
        pass

def write_particles(filename, particles):
	with open(filename, 'w', newline='') as csvfile:
		w = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
		w.writerow(['cx', 'cy', 'area', 'eqidiam'])
		w.writerow(['µm', 'µm', 'µm²', 'µm'])
		for p in particles:
			w.writerow(p)

def detect_image(det, infile, outfile, csvfile):
	img = cv2.imread(infile, cv2.IMREAD_COLOR)
	out, particles = det.detect(img, True)
	data = [pixel_to_µm(p, 1.5, 1.5) for p in particles]
	write_particles(csvfile, data)
	cv2.imwrite(outfile, out)
