import time
import cv2
import numpy as np
import partdetect
import detector
from detector import detect_image, detect_video, transcode
import os.path
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory
from camera import CameraEvents, draw_passe_partout, get_camera_parameters, create_camera
from recordings import Recordings
from motiondetect import MotionDetector
from sysinfo import get_temperature, get_disk_free

app = Flask(__name__)
app.config.from_pyfile('config.py')

status_text = "Ready"

class CamEvents(CameraEvents):
    def __init__(self, recordings):
        self.recordings = recordings

    def set_name_desc_trigger_info(self, name, description, trigger):
        self.name        = name
        self.description = description
        self.trigger     = trigger

    def video_start_recording(self, camera):
        global status_text
        self.recording = self.recordings.start_recording(self.name, self.description, self.trigger, camera)
        status_text = "Start video recording ..."
        return self.recording.make_file_path()

    def video_end_recording(self, camera):
        global status_text
        status_text = "Video recording ended"
        self.recordings.end_recording(self.recording)

    def image_start_capture(self, camera):
        self.capture = self.recordings.start_capture_still_image(self.name, self.description, self.trigger, camera)
        return self.capture.make_file_path()

    def image_end_capture(self, camera):
        global status_text
        status_text = "Image captured"
        self.recordings.end_capture_still_image(self.capture)

pdetector       = partdetect.ParticleDetector()
recorded_files  = Recordings(app.config['RECORDING_FOLDER'])
camevents       = CamEvents(recorded_files)
mdetector       = MotionDetector(app.config['MOTION_THRESHOLD'])
camera          = create_camera(app.config['CAMERA_MODULE'], camevents, mdetector, app.config['VIDEO_SIZE'], app.config['STREAM_SIZE'])

def generate_video(camera):
    video_size = app.config['VIDEO_SIZE']
    while True:
        time.sleep(0.05)
        output = camera.get_stream_image()
        if pdetector is not None:
            output, particles = pdetector.detect(output, True)
        output = draw_passe_partout(output, video_size, camera.get_ruler_length(), camera.get_ruler_xres(), camera.get_passe_partout_h(), camera.get_passe_partout_v())
        ret, buffer = cv2.imencode(".jpeg", output)
        if not ret:
            continue
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_stream')
def video_stream():
    return Response(generate_video(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download/<ident>')
def download(ident):
    filename = recorded_files.get_file(ident)
    print("download ", filename)
    if recorded_files.get_recording(ident).is_video():
        rf = app.config['RECORDING_FOLDER']
        outfile = filename + ".mp4"
        print("download ", outfile)
        if not os.path.exists(os.path.join(rf, outfile)):
            transcode(os.path.join(rf, filename), os.path.join(rf, outfile))
        return send_from_directory(app.config['RECORDING_FOLDER'], outfile, as_attachment=True)
    else:
        return send_from_directory(app.config['RECORDING_FOLDER'], filename, as_attachment=True)

@app.route('/download_detect/<ident>')
def download_detect(ident):
    rf = app.config['RECORDING_FOLDER']
    outfile = recorded_files.get_detect_file(ident)
    filename = recorded_files.get_file(ident)
    csvfile = recorded_files.get_detect_csv_file(ident)
    sx = camera.get_ruler_xres()
    sy = camera.get_ruler_yres()
    if recorded_files.get_recording(ident).is_video():
        if os.path.exists(os.path.join(rf, outfile+".mp4")):
            print("already exists: ", outfile+".mp4")
            return send_from_directory(app.config['RECORDING_FOLDER'], outfile+".mp4", as_attachment=True)
        detect_video(pdetector, os.path.join(rf, filename), os.path.join(rf, outfile+".mp4"), os.path.join(rf, csvfile), sx, sy)
        return send_from_directory(app.config['RECORDING_FOLDER'], outfile+".mp4", as_attachment=True)
    else:
        detect_image(pdetector, os.path.join(rf, filename), os.path.join(rf, outfile), os.path.join(rf, csvfile), sx, sy)
        return send_from_directory(app.config['RECORDING_FOLDER'], outfile, as_attachment=True)

@app.route('/download_detect_csv/<ident>')
def download_detect_csv(ident):
    csvfile = recorded_files.get_detect_csv_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], csvfile, as_attachment=True)

@app.route('/player/<ident>')
def player(ident):
    rec = recorded_files.get_recording(ident)
    return render_template('player.html', recording=rec)

@app.route('/detector/<ident>')
def detector(ident):
    rec = recorded_files.get_recording(ident)
    return render_template('detect.html', recording=rec)

@app.route('/delete_recording/<ident>')
def delete_recording(ident):
    ok = recorded_files.delete_recording(ident)
    if ok:
        return jsonify(result=True, stext=f"Recording '{ident}' deleted")
    else:
        return jsonify(result=False, stext=f"Unable to delete recording: '{ident}'")

@app.route('/record_video')
def record_video():
    global camera
    global camevents
    name        = request.args.get('name')
    description = request.args.get('description')
    trigger     = request.args.get('trigger')
    if not name:
        name = "Movie"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description, trigger)
    if camera.is_recording():
        return jsonify(result=False, stext="Already recording!")
    if trigger == 'manual':
        camera.record_video_manual()
    elif trigger == 'motion':
        camera.record_video_motion()
    else:
        return jsonify(result=False, stext="Invalid trigger!")
    return jsonify(result=True, stext="Recording video...", id=camevents.recording.id())

@app.route('/stop')
def stop():
    global camera
    global camevents
    if camera.is_recording():
        camera.stop_recording()
        return jsonify(result=True, stext="Recording stopped!",
            id=camevents.recording.id(),
            name=camevents.recording.meta['name'], description=camevents.recording.meta['description'], datetime=camevents.recording.meta['datetime'])
    else:
        return jsonify(result=False, stext="Not recording!")

@app.route('/capture_still_image')
def capture_still_image():
    global camera
    global camevents
    name         = request.args.get('name')
    description  = request.args.get('description')
    trigger      = request.args.get('trigger')
    if not name:
        name = "Image"
    if not description:
        description = "(no description provided)"
    camevents.set_name_desc_trigger_info(name, description, trigger)
    camera.capture_still_image()
    return jsonify(result=True, stext="Still image captured!",
            id=camevents.capture.id(),
            name=camevents.capture.meta['name'], description=camevents.capture.meta['description'], datetime=camevents.capture.meta['datetime'])

@app.route('/recording_state')
def recording_state():
    mode = "playback"
    if camera.is_recording():
        mode = "recording"
    data = {
        'mode': mode,
        'stext': status_text
    }
    return jsonify(data)

@app.route('/system_state')
def system_state():
    global status_text
    total, used, free = get_disk_free()
    temp = get_temperature()
    data = {
        "temperature": temp,
        "disk": {
            "total": total,
            "used": used,
            "free": free
        },
        'recording': {
            'stext': status_text
        }
    }
    return jsonify(data)

@app.route('/set_param/<param>')
def set_param(param):
    value = float(request.args.get('value'))
    if param == "iso":
        camera.set_iso(int(value))
    elif param == "brightness":
        camera.set_brightness(int(value))
    elif param == "contrast":
        camera.set_contrast(int(value))
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
        return jsonify({"result": False, "stext": f"Unknown parameter {param}"})
    return jsonify({"result": True, "stext": f"Parameter {param} set"})    

@app.route('/get_params')
def get_params():
    global camera
    data = {}
    get_camera_parameters(data, camera)

    if pdetector is not None:
        data['detector_threshold'] = pdetector.get_threshold()

    return jsonify(data)

@app.route('/')
def index():
    global recorded_files
    return render_template('index.html', title='RPiMicroscope', rectable=recorded_files)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    camera.start()
    camera.load_state(app.config['CAMERA_SETTINGS'])
    app.run(host='0.0.0.0') #debug=True)
    camera.save_state(app.config['CAMERA_SETTINGS'])
    camera.stop()
