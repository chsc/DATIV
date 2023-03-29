import enum
import json

class Mode(enum.Enum):
    MEASURE_OFF   = 0
    MEASURE       = 1

def get_pmsensor_parameters(data, pmsensor):
    data['measure_interval'] = pmsensor.get_measure_interval()

def set_camera_parameters(data, camera):
    camera.set_measure_interval(data['measure_interval'])

class PMSensorEvents:
    def __init__(self):
        pass

    def start_measuring(self, pmsensor):
        return ''

    def end_measuring(self, pmsensor):
        pass

class PMSensor:
    def save_state(self, filename):
        data = {}
        get_camera_parameters(data, self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent = 4)

    def load_state(self, filename):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            data = json.load(f)
            set_camera_parameters(data, self)

def create_pmsensor(modname, pmevents, measure_interval, device):
    module = __import__(modname)
    sensor = module.MPMSensor(pmevents, measure_interval, device)
    return sensor
