import time
import cv2
import numpy as np
import partdetect
import detector
import sysinfo
import requests
import os.path
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory
import flask_cors
from detector import get_det_parameters
from camera import CameraEvents, draw_passe_partout, zoom_image, get_camera_parameters, create_camera
from recordings import Recordings

app = Flask(__name__)
flask_cors.CORS(app)
app.config.from_pyfile('config.py')

status_text = "Ready"

class CamEvents(CameraEvents):
    def __init__(self, recordings):
        self.recordings = recordings

    def set_name_desc_trigger_info(self, name, description):
        self.name        = name
        self.description = description

    def video_start_recording(self, camera):
        global status_text
        self.recording = self.recordings.start_recording(self.name, self.description, camera)
        status_text = "Start video recording ..."
        return self.recording.make_file_path()

    def video_end_recording(self, camera):
        global status_text
        status_text = "Video recording ended"
        self.recordings.end_recording(self.recording)

    def image_start_capture(self, camera):
        self.capture = self.recordings.start_capture_still_image(self.name, self.description, camera)
        return self.capture.make_file_path()

    def image_end_capture(self, camera):
        global status_text
        status_text = "Image captured"
        self.recordings.end_capture_still_image(self.capture)
        
    def image_sequence_start_capture(self, camera):
        self.imgseq_capture = self.recordings.start_image_sequence(self.name, self.description, camera)
        return self.imgseq_capture.make_file_path()

    def image_sequence_end_capture(self, camera):
        global status_text
        status_text = "Image sequence captured"
        self.recordings.end_image_sequence(self.imgseq_capture)
        
    def objdet_start(self, camera):
        global status_text
        status_text = "Running object detection"
        return "file.csv"
        
    def objdet_end(self, camera):
        global status_text
        status_text = "Object detection stopped"

pdetector       = None
detectorstr     = "-"
resmodestr      = f"{app.config['CAMERA_SIZE'][0]}x{app.config['CAMERA_SIZE'][1]},{app.config['CAMERA_SENSOR_MODE']}"
recorded_files  = Recordings(app.config['RECORDING_FOLDER'])
camevents       = CamEvents(recorded_files)
camera          = create_camera(app.config['CAMERA_MODULE'], camevents, app.config['CAMERA_SIZE'], app.config['STREAM_SIZE'], app.config['CAMERA_SEQUENCE_FPS'], app.config['CAMERA_SENSOR_MODE'])


def generate_video(camera):
    video_size = app.config['CAMERA_SIZE']
    while True:
        time.sleep(0.05)
        output = camera.get_stream_image()
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        if pdetector is not None:
            output, parts = pdetector.detect(output, True)
        else:
            output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
        output = draw_passe_partout(output, video_size, camera.get_ruler_length(), camera.get_ruler_xres(), camera.get_passe_partout_h(), camera.get_passe_partout_v())
        output = zoom_image(output, camera.get_zoom())
        ret, buffer = cv2.imencode(".jpeg", output)
        if not ret:
            continue
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/set_date')
def set_date():
    value = (request.args.get('value')) # unquote_plus
    if sysinfo.set_time(value):
        return jsonify({"result": True , "status_text": f"Date set to: {value}"})    
    return jsonify({"result": False, "status_text": f"Date not set to: {value}"})    

@app.route('/set_resolution_and_mode')
def set_resolution_and_mode():
    global resmodestr
    v = request.args.get('value')
    rm = v.split(',')
    if len(rm) != 2:
        return jsonify({"result": False , "status_text": f"Invalid mode: {v}"})
    res = rm[0].split('x')
    if len(res) != 2:
        return jsonify({"result": False , "status_text": f"Invalid resolution: {v}"})
    if camera.set_resolution_and_mode((int(res[0]), int(res[1])), int(rm[1])):
        resmode = v
        return jsonify({"result": True, "status_text": f"Resolution {camera.get_resolution()} set ({camera.get_fps()}, {camera.camera.sensor_mode})"})
    return jsonify({"result": False , "status_text": f"Unable to set resolution: {res}"})

@app.route('/get_resolution_and_mode')
def get_resolution_and_mode():
    global camera, resmodestr
    return jsonify({"resmode": resmodestr})

@app.route('/set_detector')
def set_detector():
    global pdetector, detectorstr
    v = request.args.get('value')
    if v == "threshold":
        pdetector = partdetect.ParticleDetectorThreshold()
    elif v == "difference":
        pdetector = partdetect.ParticleDetectorDifference()
    elif v == "-":
        pdetector = None
    else:
        return jsonify({"result": False , status_text: f"Unable to set detector: {v}"})
    detectorstr = v
    return jsonify({"result": True , status_text: f"Detector {v} set."})

@app.route('/get_detector')
def get_detector():
    global detectorstr
    return jsonify({"detector": detectorstr})

@app.route('/video_stream')
def video_stream():
    return Response(generate_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download/<ident>')
def download(ident):
    filename = recorded_files.get_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename, as_attachment=True)

@app.route('/download_meta/<ident>')
def download_meta(ident):
    filename = recorded_files.get_meta_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename, as_attachment=True)

@app.route('/player/<ident>')
def player(ident):
    rec = recorded_files.get_recording(ident)
    return render_template('player.html', recording=rec)

@app.route('/delete_recording/<ident>')
def delete_recording(ident):
    ok = recorded_files.delete_recording(ident)
    if ok:
        return jsonify(result=True, status_text=f"Recording '{ident}' deleted")
    else:
        return jsonify(result=False, status_text=f"Unable to delete recording: '{ident}'")


@app.route('/record_video')
def record_video():
    global camera
    global camevents
    name        = request.args.get('name')
    description = request.args.get('description')
    if not name:
        name = "Movie"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description)
    if camera.is_recording():
        return jsonify(result=False, status_text="Already recording!")
    if camera.record_video():
        return jsonify(result=True, status_text="Recording video...", id=camevents.recording.id())
    else:
        return jsonify(result=False, status_text="Unable to record video! Check size! 1080p is maximum!")

@app.route('/stop_record_video')
def stop_record_video():
    global camera
    global camevents
    if camera.is_recording():
        camera.stop_recording()
        return jsonify(
            result=True,
            status_text="Recording stopped!",
            id = camevents.recording.id(),
            name = camevents.recording.meta['name'],
            description = camevents.recording.meta['description'],
            datetime = camevents.recording.meta['datetime'])
    else:
        return jsonify(result=False, status_text="Not recording!")


@app.route('/capture_image_sequence')
def capture_image_sequence():
    global camera
    global camevents
    name        = request.args.get('name')
    description = request.args.get('description')
    if not name:
        name = "Sequence"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description)
    if camera.is_recording():
        return jsonify(result=False, status_text="Already recording!")
    camera.capture_image_sequence()
    return jsonify(result = True,
        status_text = "Recording video...",
        id = camevents.imgseq_capture.id())

@app.route('/stop_capture_image_sequence')
def stop_capture_image_sequence():
    global camera
    global camevents
    if camera.is_recording():
        camera.stop_capture_image_sequence()
        return jsonify(result=True,
            status_text = "Recording stopped!",
            id = camevents.imgseq_capture.id(),
            name = camevents.imgseq_capture.meta['name'],
            description = camevents.imgseq_capture.meta['description'],
            datetime = camevents.imgseq_capture.meta['datetime'])
    else:
        return jsonify(result=False, status_text="Not recording!")

@app.route('/detect_objects')
def detect_objects():
    global camera
    global camevents
    name        = request.args.get('name')
    description = request.args.get('description')
    if not name:
        name = "Sequence"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description)
    if camera.is_recording():
        return jsonify(result=False, status_text="Already recording!")
    camera.detect_objects()
    return jsonify(result = True,
        status_text = "Recording video...",
        id = camevents.imgseq_capture.id())

@app.route('/stop_detect_objects')
def stop_detect_objects():
    global camera
    global camevents
    if camera.is_recording():
        camera.stop_detect_objects()
        return jsonify(result = True,
            status_text = "Recording stopped!",
            id = camevents.imgseq_capture.id(),
            name = camevents.imgseq_capture.meta['name'],
            description = camevents.imgseq_capture.meta['description'],
            datetime = camevents.imgseq_capture.meta['datetime'])
    else:
        return jsonify(result=False, status_text="Not recording!")


@app.route('/capture_still_image')
def capture_still_image():
    global camera
    global camevents
    name         = request.args.get('name')
    description  = request.args.get('description')
    if not name:
        name = "Image"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description)
    camera.capture_still_image()
    return jsonify(result=True,
            status_text = "Still image captured!",
            id = camevents.capture.id(),
            name = camevents.capture.meta['name'],
            description = camevents.capture.meta['description'],
            datetime = camevents.capture.meta['datetime'])

@app.route('/recording_state')
def recording_state():
    mode = "playback"
    print(camera.is_recording())
    if camera.is_recording():
        mode = "recording"
    data = {
        'mode': mode,
        'status_text': status_text
    }
    return jsonify(data)

@app.route('/system_state')
def system_state():
    global status_text
    total, used, free = sysinfo.get_disk_free()
    temp = sysinfo.get_temperature()
    hostname = sysinfo.get_hostname()
    data = {
        'hostname': hostname,
        "temperature": temp,
        "disk": {
            "total": total,
            "used": used,
            "free": free
        },
        'recording': {
            'status_text': status_text
        }
    }
    return jsonify(data)

@app.route('/set_param/<param>')
def set_param(param):
    global pdetector
    value = float(request.args.get('value'))
    if param == "res_width":
        camera.set_width(int(value))
    elif param == "res_height":
        camera.set_height(int(value))
    elif param == "shutter_speed":
        camera.set_shutter_speed(int(value))
    elif param == "iso":
        camera.set_iso(int(value))
    elif param == "brightness":
        camera.set_brightness(int(value))
    elif param == "contrast":
        camera.set_contrast(int(value))
    elif param == "zoom":
        camera.set_zoom(int(value))
    elif param == "ruler_xres":
        camera.set_ruler_xres(value)
    elif param == "ruler_yres":
        camera.set_ruler_yres(value)
    elif param == "ruler_length":
        camera.set_ruler_length(value)
    elif param == "passe_partout_h":
        camera.set_passe_partout_h(value)
    elif param == "passe_partout_v":
        camera.set_passe_partout_v(value)
    elif param == "detector_threshold":
        if pdetector is not None:
            pdetector.set_threshold(value)
    else:
        return jsonify({"result": False, status_text: f"Unknown parameter {param}"})
    return jsonify({"result": True, status_text: f"Parameter {param} set"})    

@app.route('/get_params')
def get_params():
    global camera
    data = {}
    get_camera_parameters(data, camera)
    get_det_parameters(data, pdetector)
    return jsonify(data)

@app.route('/')
def index():
    global recorded_files
    return render_template('index.html', title=sysinfo.get_hostname(), rectable=recorded_files)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    #register_camera(app)
    camera.start()
    camera.load_state(app.config['CAMERA_SETTINGS'])
    app.run(host='0.0.0.0') #debug=True)
    camera.save_state(app.config['CAMERA_SETTINGS'])
    camera.stop()

