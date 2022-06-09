import math

breath_in_volume = 500            # cm³
breath_in_time = 4                # seconds
inlet_diagonal = 11               # cm
light_curtain_width = 15          # mm

volumetric_flow_rate = breath_in_volume / breath_in_time  # vol. flow rate is Q
inlet_area = inlet_diagonal**2 / 4 * math.pi
flow_speed = volumetric_flow_rate / inlet_area

def calc_cuboid_volume(w, h):
    v = w * h * light_curtain_width 
    return v / 1000 # convert to cm³

def calc_cylinder_volume(diagonal, d):
    v = diagonal**2 / 4 * math.pi * light_curtain_width
    return v / 1000 # convert to cm³

def calc_particle_flow_rate(particles, volume):
    # particles per volume
    sigma = particles / volume
    # use flow rate to calc particle flow rate
    return sigma * volumetric_flow_rate


if __name__ == "__main__":
	print("inlet area:", inlet_area, "cm²")
	print("flow speed:", flow_speed, "cm/s")

	volume = calc_cuboid_volume(85.5, 65, 15)
	print("volume:", volume, "cm³")

	pf = calc_particle_flow_rate(100, volume)
	print("particle flow rate:", pf, "particles/s")
