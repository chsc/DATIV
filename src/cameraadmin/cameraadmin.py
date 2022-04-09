import flask
import flask_cors
import camnetwork

copyright = "Copyright (C) 2021"

app = flask.Flask(__name__, static_folder='../static', template_folder='../templates')
flask_cors.CORS(app)
app.config.from_pyfile('config.py')

cnetwork = camnetwork.CameraNetwork(app.config['CAMERA_PORT'], app.config['CAMERA_IP_TEMPL'], app.config['CAMERA_IP_RANGE'])

@app.route('/get_hosts')
def get_hosts():
    return flask.jsonify(cnetwork.get_hosts())

@app.route('/overview')
def overview():
    return flask.render_template('overview.html', title='RPiMicroscope', camnetwork=cnetwork, copyright=copyright)

@app.route('/')
def index():
    return flask.render_template('camnetwork.html', title='RPiMicroscope', camnetwork=cnetwork, copyright=copyright)

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory('../static', 'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    cnetwork.load_cameras(app.config['CAMERA_HOST_FILE'])
    app.run(host='0.0.0.0', port=app.config['PORT']) #debug=True)
    
