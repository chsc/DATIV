import cv2
import numpy as np
import datetime
import time
import csv
import picamera
from detector import count_frames

class MyOutput(object):
    def __init__(self):
        pass
        
    def write(self, s):
        #print("recimage", len(s))
        return len(s)
        
    def flush(self):
        pass
        
out = MyOutput()
        
def generator(images):
    global stop
    while True:
        if images == 0:
            return
        images -= 1
        yield out 

def vbenchmark(fname, wr, res, fps, fmt):
    c = picamera.PiCamera(resolution=res, framerate=fps)
    time.sleep(2)
    
    basef = f'{fname}_{res[0]}x{res[1]}_{fps}fps'
    vfile = basef + ".h264"
    print('recording: ', basef)

    rectime = 10
    start = datetime.datetime.now()
    c.start_recording(out, format=fmt)
    c.wait_recording(rectime)
    c.stop_recording()
    delta = datetime.datetime.now() - start
    frames = count_frames(vfile)
    c.close()
    
    wr.writerow([f'{res[0]}x{res[1]}', fmt, fps, frames / delta.total_seconds(), rectime, delta.total_seconds(), frames])

def do_vbenchmark(fname):
    vmodes = [
        ((640, 480), 100),
        ((1280, 720), 60),
        ((1920, 1080), 30)
    ]
    fmts = [
        'yuv', 'rgb', 'raw', 'jpeg'
    ]
    
    with open('video_benchmark_' + fname + '.csv', 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, dialect='excel')
        wr.writerow(['resolution', 'framerate', 'framerate real', 'length (sec)', 'length real (sec)', 'frames'])
        for m in vmodes:
            for f in fmts:
                vbenchmark(fname, wr, m[0], m[1], f)

def ibenchmark(fname, wr, res, sm, fmt, vp):
    basef = f'{fname}_{res[0]}x{res[1]}_{fmt}_vp{vp}'
    print('image: ', basef)
    
    images = 50
    c = None
    try:
        c = picamera.PiCamera(resolution=res, sensor_mode=sm)
        c.framerate = 90
        print("sensor_mode", c.sensor_mode)
        time.sleep(2)
        start = datetime.datetime.now()
        c.capture_sequence(generator(images), format=fmt, use_video_port=vp)
        delta = datetime.datetime.now() - start
        c.close()
    except Exception as e:
        print("Error capturing", e)
        if c is not None:
            c.close()
        return 0
    
    return images / delta.total_seconds()
    
    #if delta == 0:
    #    wr.writerow([f'{res[0]}x{res[1]}', sm, fmt, vp, -1, 0, images])
    #else:
    #    wr.writerow([f'{res[0]}x{res[1]}', sm, fmt, vp, images / delta.total_seconds(), delta.total_seconds(), images])

def do_ibenchmark(fname, imodes, fmts):
    with open('image_benchmark_' + fname + '.csv', 'w', newline='') as csvfile:
        wr = csv.writer(csvfile, dialect='excel')
        wr.writerow(['Still Port'])
        wr.writerow(['resolution'] + fmts)
        for m in imodes:
            r = m[0]
            fps = []
            for f in fmts:
                sm = m[1]
                fps.append(ibenchmark(fname, wr, r, sm, f, False))
            wr.writerow([f'{r[0]}x{r[1]}'] + fps)
            
        wr.writerow(['Video Port'])
        for m in imodes:
            r = m[0]
            fps = []
            for f in fmts:
                sm = m[1]
                fps.append(ibenchmark(fname, wr, r, sm, f, True))
            wr.writerow([f'{r[0]}x{r[1]}'] + fps)
        
def test_capture(filen, vp):
    c = picamera.PiCamera(resolution=(3280, 2464), sensor_mode=0) # rpicam v2
    #c = picamera.PiCamera(resolution=(2592, 1944), sensor_mode=2) # spycam v1
    c.awb_mode = 'off'
    c.awb_gains = (1.4, 1.7)
    c.shutter_speed = 500
    time.sleep(2)
    c.capture(filen + ".png", use_video_port=vp)
    c.close()
    
def compare_vp_still(filen):
    test_capture(filen + '_videoport', True)
    test_capture(filen + '_stillport', False)
    
imodes_v1 = [
    ((2592, 1944), 2),
    ((1920, 1080), 1),
    #((2592, 1944), 3),
    ((1296, 972), 4),
    ((1296, 730), 5),
    ((640, 480), 6),
    ((640, 480), 7),
]

imodes_v2 = [
    #((3280, 2464), 2),
    ((3280, 2464), 0), # 2 or 3 does not work? ENOMEM
    ((1920, 1080), 1),
    ((1640, 1232), 4),
    ((1640, 922), 5),
    ((1280, 720), 6),
    ((640, 480), 7),
]

# HQCAM: 
# (4056, 3040),
    
fmts = [
    'yuv',
    'rgb',
    'jpeg'
]

compare_vp_still('compare_pi4_rpicamv2')

#do_vbenchmark("spycam")
#do_ibenchmark("rpicamv2_capture_sequence", imodes_v2, fmts)
