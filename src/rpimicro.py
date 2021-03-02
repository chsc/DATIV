from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory
from cvcamera import CVVideoCamera
from cvrecorder import CVVideoRecorder
from sysinfo import get_temperature, get_disk_free
from threading import Lock
from datetime import datetime
import time
import cv2
import glob
import os.path
import json

lock = Lock()

app = Flask(__name__)

app.config['RECORDING_FOLDER'] = 'recordings'

def write_video_meta_info(outfile, videofile, recname, description, datetime, trigger):
    meta = {
        'videofile': videofile,
        'recname': recname,
        'description': description,
        'datetime': datetime,
        'trigger': trigger
        }
    with open(outfile, 'w') as f:
        json.dump(meta, f, indent=4)

def read_video_meta_info(outfile):
    with open(outfile, 'r') as f:
        meta = json.load(f)
        return meta

def scan_recording_directory():
    recorded_videos = glob.glob(os.path.join(app.config['RECORDING_FOLDER'], "*.avi"))

def process_frame(frame):
    global rec
    if rec is not None:
        print("recording frame")
        rec.write(frame)

write_video_meta_info('test.json', 'vid.avi', 'bla', 'blub', "21424315", 'manual')
print(read_video_meta_info('test.json'))

vid = CVVideoCamera()
vid.run(process_frame)
rec = None

# CPU Temp!
# https://blog.heimetli.ch/sysfs-ajax-flask.html
# AJAX
# https://flask.palletsprojects.com/en/1.1.x/patterns/jquery/
# thread opencv + flask
# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

recorded_items = [dict(name='test.mov', description="A test recording..."),
                  dict(name='test.mov', description="Another test recording...")]

def generate_video(camera):
    while True:
        with lock:
            frame = camera.frame
            if frame is None:
                continue
            #output = cv2.resize(frame, (640, 480), interpolation = cv2.INTER_AREA)
            ret, buffer = cv2.imencode(".jpeg", frame)
            if not ret:
                continue
            print("imencode", ret)
            time.sleep(0.05)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_stream')
def video_stream():
    return Response(generate_video(vid), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recordings/<filename>')
def recordings(filename):
    return send_from_directory(app.config['RECORDING_FOLDER'], filename)

@app.route('/player/<filename>')
def player(filename):
    return render_template('player.html', file=filename)

n = None
d = None
is_recording = False

def build_file_name(name):
    now = datetime.now()
    return name + "_" + now.strftime("%Y-%m-%d_%H-%M-%S-%f")

@app.route('/record', methods=['POST'])
def record():
    global rec
    json = request.get_json()
    print(json)
    n = json['name']
    d = json['description']
    if rec is None:
        rec = CVVideoRecorder(build_file_name(n) + ".avi", vid.size(), int(vid.fps()))
        return jsonify(result=True, text="Recording video...")
    else:
        return jsonify(result=False, text="Already recording")

@app.route('/stop')
def stop():
    global rec
    if rec is not None:
        del rec
        rec = None
        recorded_items.append(dict(name=n, description=d))
        return jsonify(result=True)
    else:
        return jsonify(result=False)

@app.route('/temperature')
def temperature():
    return jsonify({"temperature": get_temperature() })

@app.route('/diskfree')
def diskfree():
    total, used, free = get_disk_free()
    return jsonify({"total": total, "used": used, "free": free })

@app.route('/')
def index():
    return render_template('index.html', title='RPiMicroscope', rectable=recorded_items)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host= '0.0.0.0')#debug=True)
    vid.stop()
