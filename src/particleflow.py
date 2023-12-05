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

import math
import json

tidal_volume = 500            # cm³
breath_freq  = 15             # breathing frequency in breaths per minute
inlet_diagonal = 11           # cm
light_curtain_width = 15      # mm

volumetric_flow_rate = 0
inlet_area = 0
flow_speed = 0

def calc_parameters():
    global tidal_volume, breath_freq, inlet_diagonal
    global volumetric_flow_rate, inlet_area, flow_speed
    volumetric_flow_rate = tidal_volume / ( 60 / breath_freq)  # vol. flow rate is Q
    inlet_area = inlet_diagonal**2 / 4 * math.pi
    flow_speed = volumetric_flow_rate / inlet_area
    
def set_breath_params(tv, bfreq):
    global tidal_volume, breath_freq
    tidal_volume = tv
    breath_freq = bfreq
    save()
    
def save():
    global tidal_volume, breath_freq, inlet_diagonal, light_curtain_width
    data = {
    "tidal_volume": tidal_volume,
    "breath_freq": breath_freq,
    "inlet_diagonal": inlet_diagonal,
    "light_curtain_width" : light_curtain_width
    }
    with open("particle_flow_settings.json", 'w') as f:
        json.dump(data, f, indent = 4)

def load():
    global tidal_volume, breath_freq, inlet_diagonal, light_curtain_width
    with open("particle_flow_settings.json", 'r') as f:
        data = json.load(f)
    tidal_volume = data['tidal_volume']
    breath_freq = data['breath_freq']
    inlet_diagonal = data['inlet_diagonal']
    light_curtain_width = data['light_curtain_width']
    calc_parameters()

def calc_cuboid_volume(w, h):
    v = w * h * light_curtain_width 
    return v / 1000 # convert to cm³

def calc_cylinder_volume(diagonal, d):
    v = diagonal**2 / 4 * math.pi * light_curtain_width
    return v / 1000 # convert to cm³

def calc_particle_flow_rate(particles, volume):
    # particles per volume [p/cm³]
    n = particles / volume
    # use flow rate to calc particle flow rate
    return n * volumetric_flow_rate


if __name__ == "__main__":
    #save()
    load()
    
    print("inlet area:", inlet_area, "cm²")
    print("flow speed:", flow_speed, "cm/s")

    volume = calc_cuboid_volume(85.5, 65)
    print("volume:", volume, "cm³")

    pf = calc_particle_flow_rate(6, volume)
    print("particle flow rate:", pf, "particles/s")
