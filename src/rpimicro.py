import time
import cv2
import numpy as np
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
    video_size = app.config['VIDEO_SIZE']
    while True:
        output = None
        with camera.lock:
            frame = camera.frame
            if frame is None:
                continue
            output = cv2.resize(frame, stream_size, interpolation = cv2.INTER_AREA)
        sx = stream_size[0]
        sy = stream_size[1]
        vx = video_size[0]
        vy = video_size[1]
        px = sx / 2 * 0.25
        py = sy / 2 * 0.25
        pts = np.array([[px, py], [sx-px, py], [sx-px, sy-py], [px, sy-py]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        output = cv2.polylines(output, [pts], True, (0, 0, 128), 1)
        xscale = sx / vx
        ruler_len = int(camera.get_ruler_length() / camera.get_ruler_xres() * xscale)
        #print(camera.get_ruler_xres(), camera.get_ruler_length(), xscale, ruler_len)
        output = cv2.line(output, (10, sy-10), (10+ruler_len, sy-10), (0, 255, 0), 1)
        output = cv2.line(output, (10, sy-11), (10, sy-9), (0, 255, 0), 1)
        output = cv2.line(output, (10+ruler_len, sy-11), (10+ruler_len, sy-9), (0, 255, 0), 1)
        ret, buffer = cv2.imencode(".jpeg", output)
        if not ret:
            continue
        time.sleep(0.05)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_stream')
def video_stream():
    return Response(generate_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download/<ident>')
def download(ident):
    filename = recorded_files.get_file(ident)
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
    name         = json['name']
    d            = json['description']
    t            = json['trigger']
    ruler_xres   = camera.get_ruler_xres()
    ruler_yres   = camera.get_ruler_yres()
    iso          = camera.get_iso()
    brightness   = camera.get_brightness()
    contrast     = camera.get_contrast()
    if not name:
        name = "Movie"
    if not d:
        d = "(no description provided)"
    if camera.recorder is None:
        recording = recorded_files.start_recording(name, d, t, iso, brightness, contrast, ruler_xres, ruler_yres)
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

@app.route('/capture_still_image')
def capstill():
    global recorded_files

    name         = request.args.get('name')
    description  = request.args.get('description')

    if not name:
        name = "Image"
    if not description:
        description = "(no description provided)"

    iso          = camera.get_iso()
    brightness   = camera.get_brightness()
    contrast     = camera.get_contrast()
    ruler_xres   = camera.get_ruler_xres()
    ruler_yres   = camera.get_ruler_yres()

    capture = recorded_files.start_capture_still_image(name, description, iso, brightness, contrast, ruler_xres, ruler_yres)
    camera.capture_still_image(capture.make_image_path(recorded_files.recdir))
    recorded_files.end_capture_still_image(capture)

    return jsonify(result=True, stext="Still imeage captured!")

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
    value = float(request.args.get('value'))
    if param == "iso":
        camera.set_iso(value)
    elif param == "brightness":
        camera.set_brightness(value)
    elif param == "contrast":
        camera.set_contrast(value)
    elif param == "ruler_xres":
        camera.set_ruler_xres(value)
    elif param == "ruler_yres":
        camera.set_ruler_yres(value)
    elif param == "ruler_length":
        camera.set_ruler_length(value)
    else:
        return jsonify({"result": False, "stext": f"Unknown parameter {param}"})
    return jsonify({"result": True, "stext": f"Parameter {param} set"})    

@app.route('/get_params')
def get_params():
    data = {
        "iso": camera.get_iso(),
        "brightness": camera.get_brightness(),
        "contrast": camera.get_contrast(),
        "ruler_xres": camera.get_ruler_xres(),
        "ruler_yres": camera.get_ruler_yres(),
        "ruler_length": camera.get_ruler_length()
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

