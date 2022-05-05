import cv2
import numpy as np
import datetime
import time
import csv
import os
import picamera
import zipfile
import io
from threading import Thread, Lock
from camera import Camera, CameraEvents, Mode
from detector import detect_image, detect_video, transcode, count_frames

# https://picamera.readthedocs.io/en/release-1.10/index.html

class YuvFpsOutput(object):
    def __init__(self, camera, size, fps):
        self.camera = camera
        self.size = size
        self.delta = 1.0 / fps
        self.cnt = 0
        self.tprev = -1
        self.adt = 0
        
    def write(self, buffer):
        print("size", self.size)
        fw = (self.size[0] + 31) // 32 * 32
        fh = (self.size[1] + 15) // 16 * 16
        ydata = np.frombuffer(buffer, dtype=np.uint8, count=fw*fh).reshape(fh, fw)
        if self.tprev == -1:
            self.tprev = time.time()
            self.tstart = self.tprev
            self.start()
            self.frame(ydata, 0.0, 0)
        else:
            dt = time.time() - self.tprev
            self.adt += dt
            self.tprev = time.time()
            fps = 1.0 / dt
            if self.adt >= self.delta:
                self.adt -= self.delta
                self.cnt += 1
                self.frame(ydata, self.tprev - self.tstart, self.cnt)
                
    def flush(self):
        pass
        
    def start(self):
        pass
        
    def frame(self, ydata, t, cnt):
        pass
    
class YuvOutput(object):
    def __init__(self, camera, size):
        self.camera = camera
        self.size = size
        self.cnt = 0
        
    def write(self, buffer):
        print("size", self.size)
        fw = (self.size[0] + 31) // 32 * 32
        fh = (self.size[1] + 15) // 16 * 16
        ydata = np.frombuffer(buffer, dtype=np.uint8, count=fw*fh).reshape(fh, fw)
        if self.cnt == 0:
            self.tstart = time.time()
            self.start()
            self.frame(ydata, 0.0, 0)
        else:
            self.frame(ydata, time.time() - self.tstart, self.cnt)
        self.cnt += 1
                
    def flush(self):
        pass
        
    def start(self):
        pass
        
    def frame(self, ydata, t, cnt):
        pass

class ImgSeqOutput(YuvFpsOutput):
    def __init__(self, camera, size, fps, fname):
        YuvFpsOutput.__init__(self, camera, size, fps)
        self.zipf = zipfile.ZipFile(fname, mode='w', compression=zipfile.ZIP_DEFLATED)
        self.csvstr = io.StringIO()
        self.csvwr = csv.writer(self.csvstr)
    
    def __del__(self):
        self.zipf.writestr(f"timings.csv", self.csvstr.getvalue())
        
    def start(self):
        self.csvwr.writerow(['image', 'time'])
        self.csvwr.writerow(['[nr]', '[s]'])
        
    def frame(self, ydata, t, cnt):
        #print('frame', t, cnt)
        r, buf = cv2.imencode('.png', ydata)
        self.zipf.writestr(f"{cnt}.png", buf)
        self.csvwr.writerow([cnt, t])
        
class ObjDetOutput(YuvOutput):
    def __init__(self, camera, odet, size, fname):
        YuvOutput.__init__(self, camera, size)
        self.zipf = zipfile.ZipFile(fname, mode='w', compression=zipfile.ZIP_DEFLATED)
        self.csvstr = io.StringIO()
        self.csvwr = csv.writer(self.csvstr)
        self.odet = odet
    
    def __del__(self):
        self.zipf.writestr(f"objects.csv", self.csvstr.getvalue())
        
    def start(self):
        self.csvwr.writerow(['image', 'time', 'bx', 'by', 'bw', 'bh', 'cx', 'cy', 'area'])
        self.csvwr.writerow(['[nr]', '[s]', '[px]', '[px]', '[px]', '[px]', '[px]', '[px]', '[px²]'])
        
    def frame(self, ydata, t, cnt):
        #r, buf = cv2.imencode('.png', ydata)
        #self.zipf.writestr(f"{cnt}.png", buf)
        
        _, dobjs = self.odet.detect(ydata, False)
        for dobj in dobjs:
            bx, by, bw, bh, cx, cy, area = dobj;
            self.csvwr.writerow([cnt, t, bx, by, bw, bh, cx, cy, area])
        

class MCamera(Camera):
    def __init__(self, camevents, camera_size, stream_size, seqfps, smode):
        self.lock = Lock()
        self.frame = None
        self.running = False
        self.mode = Mode.RECORD_OFF
        # Events
        self.camevents = camevents
        # sizes
        self.camera_size = camera_size
        self.stream_size = stream_size
        self.stream_image = None
        self.cached_image = False
        # Parameters
        self.ruler_length = 200
        self.ruler_xres = 5
        self.ruler_yres = 5
        self.passe_partout_h = 25
        self.passe_partout_v = 25
        self.zoom = 100
        self.seqfps = seqfps
        
        # Pi Camera
        self.camera = picamera.PiCamera(resolution=camera_size, sensor_mode=smode)
        #self.camera.exposure_mode = 'off' auto
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = (1.4, 1.7)
        #self.camera.led = True

        print('default camera resolution:', self.get_resolution())
        print('framerate:', self.get_fps())
        
    def __del__(self):
        self.close()
    
    def close(self):
        self.camera.close()

    #def _camera_recording_thread(self):
    #    while self.running:
    #        with self.lock:
    #            if self.mode != Mode.RECORD_OFF:
    #                self.camera.wait_recording(0.5)
    #                print('wait recording')
    #        time.sleep(1)
            
    #def _start(self):
    #    self.running = True
    #    t = Thread(target=self._camera_recording_thread)
    #    t.daemon = True
    #    t.start()

    #def _stop(self):
    #    self.running = False
    
    def set_resolution_and_mode(self, res, mode):
        with self.lock:
            try:
                self.close()
                time.sleep(0.5)
                self.camera = picamera.PiCamera(sensor_mode=mode, resolution=res)
                self.camera_size = res
                return True
            except Exception as e:
                print(str(e))
                return False
    
    def capture_still_image(self):
        with self.lock:
            try:
                if self.is_recording():
                    return False
                filename = self.camevents.image_start_capture(self)
                w, h = self.camera_size
                w = (w + 31) // 32 * 32
                h = (h + 15) // 16 * 16
                output = np.empty((h, w, 3), dtype=np.uint8)
                self.camera.capture(output, 'rgb')
                cv2.imwrite(filename, output)
                self.camevents.image_end_capture(self)
                return True
            except Exception as e:
                print(str(e))
                return False
        
    def record_video(self):
        with self.lock:
            try:
                if self.is_recording():
                    return False
                self.cached_image = True
                filename = self.camevents.video_start_recording(self)
                self.camera.start_recording(filename, format='h264', sps_timing=True)
                self.mode = Mode.RECORD
                return True
            except Exception as e:
                print(str(e))
                return False
    
    def stop_recording(self):
        with self.lock:
            try:
                if self.mode != Mode.RECORD:
                    return False
                self.camera.stop_recording()
                self.camevents.video_end_recording(self)
                self.cached_image = False
                self.mode = Mode.RECORD_OFF
                return True
            except Exception as e:
                print(str(e))
                return False

    def capture_image_sequence(self):
        with self.lock:
            try:
                if self.is_recording():
                    return False
                self.cached_image = True
                filename = self.camevents.image_sequence_start_capture(self)
                yuv_output = ImgSeqOutput(self, self.camera_size, self.seqfps, filename)
                self.camera.start_recording(yuv_output, format='yuv')
                self.mode = Mode.IMGSEQ
                return True
            except Exception as e:
                print(str(e))
                return False

    def stop_capture_image_sequence(self):
        with self.lock:
            try:
                if self.mode != Mode.IMGSEQ:
                    return False
                self.mode = Mode.RECORD_OFF
                self.camera.stop_recording()
                self.camevents.image_sequence_end_capture(self)
                self.cached_image = False
                return True
            except Exception as e:
                print(str(e))
                return False
    
    
    def detect_objects(self, odet):
        with self.lock:
            try:
                if self.is_recording():
                    return False
                self.cached_image = True
                filename = self.camevents.objdet_start(self)
                yuv_output = ObjDetOutput(self, odet, self.camera_size, filename)
                self.camera.start_recording(yuv_output, format='yuv')
                self.mode = Mode.OBJDET
                return True
            except Exception as e:
                print(str(e))
                return False

    def stop_detect_objects(self):
        with self.lock:
            try:
                if self.mode != Mode.OBJDET:
                    return False
                self.mode = Mode.RECORD_OFF
                self.camera.stop_recording()
                self.camevents.objdet_end(self)
                self.cached_image = False
                return True
            except Exception as e:
                print(str(e))
                return False


    def get_stream_image(self):
        with self.lock:
            try:
                if self.cached_image:
                    return self.stream_image
                (w, h) = self.stream_size
                image = np.empty((w * h * 3,), dtype=np.uint8)
                self.camera.capture(image, 'bgr', resize=self.stream_size, use_video_port=True)
                self.stream_image = image.reshape((h, w, 3))
                return self.stream_image
            except Exception as e:
                print(str(e))
                return self.stream_image
                
    
    def is_recording(self):
        return self.mode != Mode.RECORD_OFF

    def get_resolution(self):
        return self.camera.resolution
    
    def set_fps(self, fps):
        self.camera.framerate = fps
        
    def get_fps(self):
        return float(self.camera.framerate)
        
    def set_shutter_speed(self, shutter):
        self.camera.shutter_speed = shutter
        
    def get_shutter_speed(self):
        return self.camera.shutter_speed
        
    def set_iso(self, iso):
        self.camera.iso = iso

    def get_iso(self):
        return self.camera.iso

    def set_brightness(self, bright):
        self.camera.brightness = bright

    def get_brightness(self):
        return self.camera.brightness

    def set_contrast(self, contrast):
        self.camera.contrast = contrast

    def get_contrast(self):
        return self.camera.contrast
        
    def set_zoom(self, zoom):
        self.zoom = zoom
        
    def get_zoom(self):
        return self.zoom

    def set_ruler_xres(self, xres):
        self.ruler_xres = xres

    def get_ruler_xres(self):
        return self.ruler_xres

    def set_ruler_yres(self, yres):
        self.ruler_yres = yres

    def get_ruler_yres(self):
        return self.ruler_yres

    def set_ruler_length(self, length):
        self.ruler_length = length

    def get_ruler_length(self):
        return self.ruler_length

    def set_passe_partout_h(self, ph):
        self.passe_partout_h = ph

    def get_passe_partout_h(self):
        return self.passe_partout_h

    def set_passe_partout_v(self, pv):
        self.passe_partout_v = pv

    def get_passe_partout_v(self):
        return self.passe_partout_v








class CamEvents(CameraEvents):
    def __init__(self):
        self.vfile = 'video.mp4'
        self.ifile = 'image.png'
        self.cfile = 'data.csv'

    def video_start_recording(self, camera):
        print(f"writing to video file '{self.vfile}' ...")
        return self.vfile

    def video_end_recording(self, camera):
        print("... written to video file")

    def image_start_capture(self, camera):
        #print(f"writing to image file '{self.ifile}' ...")
        return self.ifile

    def image_end_capture(self, camera):
        #print("... written to image file")
        pass

    def objdet_start(self, camera):
        print(f"writing to csv file '{self.cfile}' ...")
        return self.cfile

    def objdet_stop(self, camera):
        print("... writing to csv file")


if __name__ == "__main__":
        
    vmodes = [
        (1, (1920, 1088), 25),
        #(2, (3280, 2464), 5),
        #(3, (3280, 2464), 5),
        (4, (1640, 1232), 25),
        (5, (1640, 922), 25),
        (6, (1280, 720), 25),
        (7, (640, 480), 90)
    ]

    def capture_still(prefix):
        cev = CamEvents()
        for m in vmodes:
            print("---------------------------------------------------------")
            basef = f'{prefix}_{m[1][0]}x{m[1][1]}_sm{m[0]}_{m[2]}fps'
            cev.vfile = basef + ".h264"
            c = MCamera(cev, MotionDetector(10), m[1], (640, 480), m[2], m[0])
            print("recording", m)
            c.record_video()
            c.camera.wait_recording(time)
            c.stop_recording()
        cev = CamEvents()
        for m in imodes:
            print("---------------------------------------------------------")
            cev.ifile = f'{prefix}_{m[1][0]}x{m[1][1]}_sm{m[0]}.png'
            c = MCamera(cev, MotionDetector(10), m[1], (640, 480), 15, m[0])
            print("capuring", m)
            c.capture_still_image()
            c.close()

    def capture_video(prefix, fps, time):
        cev = CamEvents()
        for m in vmodes:
            print("---------------------------------------------------------")
            basef = f'{prefix}_{m[1][0]}x{m[1][1]}_sm{m[0]}_{m[2]}fps'
            cev.vfile = basef + ".h264"
            c = MCamera(cev, MotionDetector(10), m[1], (640, 480), m[2], m[0])
            print("recording", m)
            c.record_video()
            c.camera.wait_recording(time)
            c.stop_recording()
            #fnr = transcode(cev.vfile, basef+".mp4", m[2])
            #print("frames transcoded", fnr, "fps recorded", fnr / time)
            c.close()
     
    #capture_still("test1")
    capture_video("test13", 25, 7)
    
    #cev = CamEvents()
    #c = MCamera(cev, MotionDetector(10), (640, 480), (640, 480), 120, 7)
    #time.sleep(1)
    
    #c.record_video()
    #c.camera.wait_recording(10)
    #c.stop_recording()
    #fnr = transcode("video.mp4", "videot.mp4", 1)
    #print("frames ", fnr)
    
    
    #c.objdet_start()
    #c.camera.wait_recording(10)
    #c.objdet_stop();
    
    #cv2.waitKey(-1)
    #c.camera.start_preview()
    #
    
    #while True:
    #    frame = vid.read()
    #    #output = cv2.resize(frame, (800, 600), interpolation = cv2.INTER_AREA)
    #    cv2.imshow('Camera - Press q for quit', frame)
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #       break
