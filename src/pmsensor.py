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

import enum
import json
import os

class Mode(enum.Enum):
    MEASURE_OFF   = 0
    MEASURE       = 1

def get_pmsensor_parameters(data, pmsensor):
    data['measure_interval'] = pmsensor.get_measure_interval()

def set_pmsensor_parameters(data, camera):
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
        get_pmsensor_parameters(data, self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent = 4)

    def load_state(self, filename):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            data = json.load(f)
            set_pmsensor_parameters(data, self)

def create_pmsensor(modname, pmevents, measure_interval, device):
    module = __import__(modname)
    sensor = module.MPMSensor(pmevents, measure_interval, device)
    return sensor
