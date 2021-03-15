import time
import cv2
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory
from cvcamera import CVVideoCamera
from recordings import Recordings
from motiondetect import MotionDetector
from sysinfo import get_temperature, get_disk_free

app = Flask(__name__)
app.config.from_pyfile('config.py')

camera          = CVVideoCamera(MotionDetector(app.config['MOTION_THRESHOLD']), app.config['VIDEO_SIZE'], app.config['STREAM_SIZE'])
recorded_files  = Recordings(app.config['RECORDING_FOLDER'])
recording       = None

def generate_video(camera):
    stream_size = app.config['STREAM_SIZE']
    while True:
        output = None
        with camera.lock:
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
    return Response(generate_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recording/<ident>')
def recording(ident):
    filename = recorded_files.get_video_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename)

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
    global recorded_files
    global recording
    global camera
    json = request.get_json()
    print(json)
    n = json['name']
    d = json['description']
    t = json['trigger']
    iso = camera.get_iso()
    brightness = camera.get_brightness()
    contrast = camera.get_contrast()
    if not n:
        n = "Movie"
    if not d:
        d = "(no description provided)"
    if camera.recorder is None:
        recording = recorded_files.start_recording(n, d, t, iso, brightness, contrast)
        camera.record(recording.make_video_path(recorded_files.recdir))
        return jsonify(result=True, stext="Recording video...")
    else:
        return jsonify(result=False, stext="Already recording")

@app.route('/stop')
def stop():
    global recorded_files
    global recording
    if camera.recorder is not None:
        camera.stop_recording()
        recorded_files.end_recording(recording)
        return jsonify(result=True, stext="Recording stopped!")
    else:
        return jsonify(result=False, stext="Not recording")

@app.route('/recording_state')
def recording_state():
    isrec = camera.recorder is not None
    mode = "playback"
    if isrec:
        mode = "recording"
    data = {
        "mode": mode,
    }
    return jsonify(data)

@app.route('/system_state')
def system_state():
    total, used, free = get_disk_free()
    temp = get_temperature()
    data = {
        "temperature": temp,
        "disk": {
            "total": total,
            "used": used,
            "free": free
        }
    }
    return jsonify(data)

@app.route('/set_param/<param>')
def set_param(param):
    value = request.args.get('value')
    if param == "iso":
        camera.set_iso(value)
    elif param == "brightness":
        camera.set_brightness(value)
    elif param == "contrast":
        camera.set_contrast(value)
    else:
        return jsonify({"result": False, "stext": f"Unknown parameter {param}"})
    return jsonify({"result": True, "stext": f"Parameter {param} set"})    

@app.route('/get_params')
def get_params():
    data = {
        "iso": camera.get_iso(),
        "brightness": camera.get_brightness(),
        "contrast": camera.get_contrast(),
    }
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html', title='RPiMicroscope', rectable=recorded_files)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    camera.playback()
    app.run(host= '0.0.0.0') #debug=True)
    camera.stop()
