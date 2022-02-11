
import csv
import cv2
import numpy

def equi_diameter(area):
	return numpy.sqrt(4 * area / numpy.pi)

def equi_perimeter(area):
	return numpy.sqrt(4 * numpy.pi * area)

def pixel_to_µm(t, sx, sy, framenr):
	(cx, cy, area) = t
	area_µm = area * sx * sy
	return (framenr, cx * sx, cy * sy, area_µm, equi_diameter(area_µm))

class Detector:
    def detect(self, image, genout):
        pass
        
def get_det_parameters(data, det):
	if det is None:
		return
	data['detector_threshold'] = det.get_threshold()

def set_det_parameters(data, det):
	if det is None:
		return
	det.set_threshold(data['detector_threshold'])

def write_particles(filename, particles):
	with open(filename, 'w', newline='') as csvfile:
		w = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
		w.writerow(['frame', 'cx', 'cy', 'area', 'eqidiam'])
		w.writerow(['-', 'µm', 'µm', 'µm²', 'µm'])
		for p in particles:
			w.writerow(p)

def detect_image(det, infile, outfile, csvfile, sx, sy):
	img = cv2.imread(infile, cv2.IMREAD_COLOR)
	out, particles = det.detect(img, True)
	data = [pixel_to_µm(p, sx, sy, 0) for p in particles]
	write_particles(csvfile, data)
	cv2.imwrite(outfile, out)

def transcode(infile, outfile, fps):
	#fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
	fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
	reader = cv2.VideoCapture(infile)
	size = (int(reader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(reader.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	#fps = reader.get(cv2.CAP_PROP_FPS)
	print("trascoding: ", infile, size, fps)
	writer = cv2.VideoWriter(outfile, fourcc, fps, size)
	fnr = 0
	while reader.isOpened():
		ret, frame = reader.read()
		if ret:
			#print("transcode frame", fnr)
			writer.write(frame)
			fnr += 1
		else:
			break
	return fnr
	
def count_frames(infile):
	reader = cv2.VideoCapture(infile)
	fnr = 0
	while reader.isOpened():
		ret, frame = reader.read()
		if ret:
			fnr += 1
		else:
			break
	return fnr

def detect_video(det, infile, outfile, csvfile, sx, sy):
	fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
	reader = cv2.VideoCapture(infile)
	size = (int(reader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(reader.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	fps = reader.get(cv2.CAP_PROP_FPS)
	writer = cv2.VideoWriter(outfile, fourcc, fps, size)
	particles = []
	fnr = 0
	while reader.isOpened():
		ret, frame = reader.read()
		if ret:
			oframe, ps = det.detect(frame, True)
			writer.write(oframe)
			print(fnr, ps)
			data = [pixel_to_µm(p, sx, sy, fnr) for p in ps]
			particles += data
			fnr += 1
		else:
			break
	write_particles(csvfile, particles)
	writer.release()
	reader.release()
