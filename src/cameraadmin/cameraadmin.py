import flask
import camnetwork

copyright = "Copyright (C) 2021"

app = flask.Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_pyfile('config.py')

cnetwork = camnetwork.CameraNetwork(app.config['PORT'])

@app.route('/register_camera')
def register_camera():
    ip       = flask.request.args.get('ip')
    hostname = flask.request.args.get('hostname')
    cnetwork.register_camera(ip, hostname)
    return flask.jsonify({"result": True, "status_text": f"Camera added"})

@app.route('/update_camera_network')
def update_camera_network():
    cnetwork.update()
    return flask.jsonify({"result": True, "status_text": f"Camera list updated"})

@app.route('/all_capture_still_image')
def all_capture_still_image():
    res, stext, results = cnetwork.broadcast('capture_still_image', None)
    return flask.jsonify({"result": res, "status_text": stext, "results": results})

@app.route('/all_record_video')
def all_record_video():
    res, stext, results = cnetwork.broadcast('record_video', None)
    return flask.jsonify({"result": res, "status_text": stext, "results": results})

@app.route('/all_stop_video')
def all_stop_video():
    ret, stext, results = cnetwork.broadcast('stop', None)
    return flask.jsonify({"result": res, "status_text": stext, "results": results})

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
    cnetwork.register_camera("127.0.0.1", "selfhost1")
    cnetwork.register_camera("127.0.0.2", "selfhost2")
    cnetwork.register_camera("127.0.0.4", "selfhost3")
    app.run(host='0.0.0.0') #debug=True)
