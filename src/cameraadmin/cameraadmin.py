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

import json
import flask
import flask_cors

app = flask.Flask(__name__, static_folder='../static', template_folder='../templates')
flask_cors.CORS(app)
app.config.from_pyfile('config.py')

title = "SANSAERO"

class CameraNetwork:
    def __init__(self, port):
        self.camera_hosts = {}
        self.port = port

    def get_hosts(self):
        return self.camera_hosts
        
    def get_port(self):
        return self.port;

    def register_camera(self, ip, hostname):
        self.camera_hosts[ip] = hostname
        
    def get_camera_link(self, ip):
        if self.port == 80:
            return f"http://{ip}";
        return f"http://{ip}:{self.port}";
    
    def save_cameras(self, filename):
         with open(filename, 'w') as f:
            json.dump(self.camera_hosts, f, indent = 4)
    
    def load_cameras(self, filename):
        with open(filename, 'r') as f:
            self.camera_hosts = json.load(f)

cnetwork = CameraNetwork(app.config['CAMERA_PORT'])

@app.route('/get_hosts')
def get_hosts():
    return flask.jsonify(cnetwork.get_hosts())
    
@app.route('/get_camera_port')
def get_camera_port():
    return flask.jsonify(cnetwork.get_port())

@app.route('/overview')
def overview():
    return flask.render_template('overview.html', title=title, camnetwork=cnetwork)

@app.route('/')
def index():
    return flask.render_template('camnetwork.html', title=title, camnetwork=cnetwork)

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory('../static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    cnetwork.load_cameras(app.config['CAMERA_HOST_FILE'])
    app.run(host='0.0.0.0', port=app.config['PORT']) #debug=True)
    
