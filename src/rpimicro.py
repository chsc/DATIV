from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory
from cvcamera import CVVideoCamera
from cvrecorder import CVVideoRecorder
from motiondetect import MotionDetector
from recordings import Recordings
from sysinfo import get_temperature, get_disk_free
from threading import Lock
import time
import cv2

# AJAX
# https://flask.palletsprojects.com/en/1.1.x/patterns/jquery/
# thread opencv + flask
# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

lock = Lock()
app = Flask(__name__)

# TODO: remove in the future
app.config['RECORDING_FOLDER'] = '../recordings'
app.config['STREAM_SIZE']      = (320, 200)
app.config['MOTION_THRESHOLD'] = 120

motion_detector = MotionDetector(app.config['MOTION_THRESHOLD'])
recorded_files  = Recordings(app.config['RECORDING_FOLDER'])
recording       = None
vid             = CVVideoCamera()
video_recorder  = None

def process_frame(frame):
    is_moving = motion_detector.detect_motion(frame)
    if is_moving:
        print("movement detected")

    global video_recorder
    if video_recorder is not None:
        print("recording frame")
        video_recorder.write(frame)

def generate_video(camera):
    stream_size = app.config['STREAM_SIZE']
    while True:
        with lock:
            frame = camera.frame
            if frame is None:
                continue
            output = cv2.resize(frame, stream_size, interpolation = cv2.INTER_AREA)
            ret, buffer = cv2.imencode(".jpeg", output)
            if not ret:
                continue
            time.sleep(0.05)
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_stream')
def video_stream():
    return Response(generate_video(vid), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recordings/<ident>')
def recordings(ident):
    filename = recorded_files.get_video_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename, mimetype='video/mjpeg')

@app.route('/player/<ident>')
def player(ident):
    rec = recorded_files.get_recording(ident)
    return render_template('player.html', recording=rec)

@app.route('/delete_recording/<ident>')
def delete_recording(ident):
    ok = recorded_files.delete_recording(ident)
    if ok:
        return jsonify(result=True, stext=f"Recording '{ident}' deleted")
    else:
        return jsonify(result=False, stext=f"Unable to delete recording: '{ident}'")

@app.route('/record', methods=['POST'])
def record():
    global video_recorder
    global recorded_files
    global recording
    json = request.get_json()
    print(json)
    n = json['name']
    d = json['description']
    t = json['trigger']
    if not n:
        n = "Movie"
    if not d:
        d = "(no description provided)"
    if video_recorder is None:
        recording = recorded_files.start_recording(n, d, t)
        video_recorder = CVVideoRecorder(recording.make_video_path(recorded_files.recdir), vid.size(), int(vid.fps()))
        return jsonify(result=True, stext="Recording video...")
    else:
        return jsonify(result=False, stext="Already recording")

@app.route('/stop')
def stop():
    global video_recorder
    global recorded_files
    global recording
    if video_recorder is not None:
        del video_recorder
        video_recorder = None
        recorded_files.end_recording(recording)
        return jsonify(result=True, stext="Recording stopped!")
    else:
        return jsonify(result=False, stext="Not recording")

@app.route('/temperature')
def temperature():
    return jsonify({"temperature": get_temperature() })

@app.route('/diskfree')
def diskfree():
    total, used, free = get_disk_free()
    return jsonify({"total": total, "used": used, "free": free })

@app.route('/set_iso', methods=['POST'])
def set_iso():
    json = request.get_json()
    print(json)
    vid.set_iso(json['iso'])
    return jsonify({"result": True, "stext": "Setting new ISO", "value": json['iso']})

@app.route('/set_brightness', methods=['POST'])
def set_brightness():
    json = request.get_json()
    print(json)
    vid.set_brightness(json['brightness'])
    return jsonify({"result": True, "stext": "Setting new brightness", "value": json['brightness']})

@app.route('/set_contrast', methods=['POST'])
def set_contrast():
    json = request.get_json()
    print(json)
    vid.set_contrast(json['contrast'])
    return jsonify({"result": True, "stext": "Setting new contrast", "value": json['contrast']})

@app.route('/')
def index():
    return render_template('index.html', title='RPiMicroscope', rectable=recorded_files)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    vid.run(process_frame)
    app.run(host= '0.0.0.0') #debug=True)
    vid.stop()
