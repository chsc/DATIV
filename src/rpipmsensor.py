"""
   Copyright 2022-2023 by Christoph Schunk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
import sysinfo
import requests
import subprocess
import os.path
from flask import Flask, Response, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file
import flask_cors
from pmsensor import PMSensorEvents, create_pmsensor
from recordings import Recordings

app = Flask(__name__)
flask_cors.CORS(app)
app.config.from_pyfile('config.py')

status_text = "Ready"

def sane_filename(fn):
    if not fn:
        return None
    return ''.join([c for c in fn if c.isalnum()]) # only alphanum!
    
class PMSEvents(PMSensorEvents):
    def __init__(self, recordings):
        self.recordings = recordings
        
    def set_name_desc_trigger_info(self, name, description):
        self.name        = name
        self.description = description

    def start_measuring(self, pmsensor):
        global status_text
        self.mespart = self.recordings.start_particle_measurement(self.name, self.description, pmsensor)
        status_text = "Measure particles ..."
        return self.mespart.make_file_path()

    def end_measuring(self, pmsensor):
        global status_text
        status_text = "Measure particles ended"
        self.recordings.end_particle_measurement(self.mespart)

pdetector       = None
recorded_files  = Recordings(app.config['RECORDING_FOLDER'])
pmsevents       = PMSEvents(recorded_files)
pmsensor        = create_pmsensor(app.config['PMSENSOR_MODULE'], pmsevents, app.config['PMSENSOR_INTERVAL'], app.config['PMSENSOR_DEVICE_BPI'])

@app.route('/set_date')
def set_date():
    value = (request.args.get('value')) # unquote_plus
    if sysinfo.set_time(value):
        return jsonify({"result": True , "status_text": "Date set to: %s" % value})
    return jsonify({"result": False, "status_text": "Date not set to: %s" % value})

@app.route('/download/<ident>')
def download(ident):
    filename = recorded_files.get_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename, as_attachment=True)

@app.route('/download_meta/<ident>')
def download_meta(ident):
    filename = recorded_files.get_meta_file(ident)
    return send_from_directory(app.config['RECORDING_FOLDER'], filename, as_attachment=True)

@app.route('/delete_recording/<ident>')
def delete_recording(ident):
    ok = recorded_files.delete_recording(ident)
    if ok:
        return jsonify(result=True, status_text="Recording '%s' deleted!" % ident)
    else:
        return jsonify(result=False, status_text="Unable to delete recording: '%s'" % ident)

@app.route('/delete_all_recordings')
def delete_all_recordings():
    ok = recorded_files.delete_all_recordings()
    if ok:
        return jsonify(result=True, status_text="All recordings deleted!")
    else:
        return jsonify(result=False, status_text="Unable to delete recordings!")

# Camera commands

@app.route('/recording_state')
def recording_state():
    data = {
        'mode': "playback",
        'status_text': status_text
    }
    return jsonify(data)

# PM Sensor commands

@app.route('/measure_particles')
def measure_particles():
    global pmsensor
    global pmsevents
    name         = sane_filename(request.args.get('name'))
    description  = request.args.get('description')
    if not name:
        name = "ParticleMeasurement"
    if not description:
        description = "(no description provided)"
    pmsevents.set_name_desc_trigger_info(name, description)
    if pmsensor.is_measuring():
        return jsonify(result=False, status_text="Already measuring!")
    if pmsensor.start():
        return jsonify(result=True,
            status_text = "Measure particles...",
            id = pmsevents.mespart.id(),
            name = pmsevents.mespart.meta['name'],
            description = pmsevents.mespart.meta['description'],
            datetime = pmsevents.mespart.meta['datetime'])
    else:
        return jsonify(result = False, status_text = "Unable to measure particles!")

@app.route('/stop_measure_particles')
def stop_measure_particles():
    global pmsensor
    global pmsevents
    if pmsensor.stop():
        return jsonify(result = True,
            status_text = "Particle measurement stopped!",
            id = pmsevents.mespart.id(),
            name = pmsevents.mespart.meta['name'],
            description = pmsevents.mespart.meta['description'],
            datetime = pmsevents.mespart.meta['datetime'])
    else:
        return jsonify(result = False, status_text="Unable to stop measure particles!")

@app.route('/particle_measurement_state')
def particle_measurement_state():
    mode = "not_measuring"
    if pmsensor.is_measuring():
        mode = "measuring"
    data = {
        'mode': mode,
        'status_text': status_text
    }
    print(data)
    return jsonify(data)

@app.route('/system_state')
def system_state():
    global status_text
    total, used, free = sysinfo.get_disk_free()
    temp = round(sysinfo.get_temperature_bpi(), 1)
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
    if param == "pms_interval":
        pmsensor.set_measure_interval(value)
    else:
        return jsonify({"result": False, "status_text": "Unknown parameter %s" % param})
    return jsonify({"result": True, "status_text": "Parameter %s set" % param})

@app.route('/get_params')
def get_params():
    data = {}
    # pms
    data["pms_interval"] = pmsensor.get_measure_interval()
    return jsonify(data)

@app.route('/')
def index():
    global recorded_files
    return render_template('pms_index.html', title=sysinfo.get_hostname(), rectable=recorded_files, version=app.config['VERSION'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')
    
@app.route('/user_manual')
def user_manual():
    return send_from_directory('static', 'doc/UserManual.pdf')
    
@app.route('/upload_firmware', methods=['GET', 'POST'])
def upload_firmware():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        folder = ".."
        file.save(os.path.join(folder, "firmware_upload.tar.gz"))
        ret = subprocess.run(['./extract_firmware.sh'], cwd=folder, stderr=subprocess.STDOUT)
        print(ret)
        os._exit(0) # exit app and force restart when run as a service
        return redirect("/")
    return '''
    <!doctype html>
    <title>Upload Firmware File</title>
    <h1>Upload Firmware File</h1>
    <form method="POST" enctype="multipart/form-data">
      <p><input type="file" name="file" accept=".tar.gz"></p>
      <p><input type="submit" value="Upload"></p>
    </form>
    '''

@app.route('/download_firmware')
def download_firmware():
    folder = ".."
    ret = subprocess.run(['./create_firmware.sh'], cwd=folder, stderr=subprocess.STDOUT)
    print(ret)
    return send_file('../firmware_rpimicro.tar.gz')


if __name__ == "__main__":
    pmsensor.load_state(app.config['PMSENSOR_SETTINGS'])
    app.run(host='0.0.0.0') #debug=True)
    pmsensor.save_state(app.config['PMSENSOR_SETTINGS'])
