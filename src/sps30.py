import serial
import struct
import time
import csv
from threading import Thread, Lock, Timer
from pmsensor import PMSensor, PMSensorEvents, Mode

"""
SPS30 Sensor
Pins:
    RED:     5V
    WHITE:   RX/SDA
    VIOLET:  TX/SCL
    GREEN:   SEL, floating for UART, pull to groeund for I2C
    BLACK:   GND
"""

def reverse_byte_stuffing(raw_data):
    if b"\x7D\x5E" in raw_data:
        raw_data = raw_data.replace(b"\x7D\x5E", b"\x7E")
    if b"\x7D\x5D" in raw_data:
        raw_data = raw_data.replace(b"\x7D\x5D", b"\x7D")
    if b"\x7D\x31" in raw_data:
        raw_data = raw_data.replace(b"\x7D\x31", b"\x11")
    if b"\x7D\x33" in raw_data:
        raw_data = raw_data.replace(b"\x7D\x33", b"\x13")
    return raw_data

def trim_data(raw_data):
    return raw_data[5:-2]

class MPMSensor(PMSensor):
    def __init__(self, pmevents, measure_interval, device):
        self.lock = Lock()
        self.pmevents = pmevents
        self.measure_interval = measure_interval
        self.mode = Mode.MEASURE_OFF
        self.device = device
        try:
            self.ser = serial.Serial(device, 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2)
            print("SPS30: product_type:", self.read_product_type())
            print("SPS30: serial_number:", self.read_serial_number())
            print("SPS30: firmware_version:", self.read_firmware_version())
            print("SPS30: status_register:", self.read_status_register())
        except serial.SerialException:
            print("SPS30: unable to open serial interface:", device)
            self.ser = None
        
    def is_measuring(self):
        return self.mode == Mode.MEASURE

    def start(self):
        if self.ser is None:
            return False
        if self.mode != Mode.MEASURE_OFF:
            return False
        self.lock.acquire()
        try:
            filename = self.pmevents.start_measuring(self)
            #self.zipf = zipfile.ZipFile(filename, mode='w', compression=zipfile.ZIP_DEFLATED)
            #self.csvio = io.StringIO()
            print('Start measuring...')
            self.csvio = open(filename, 'w', newline='', encoding='utf-8')
            self.csvwr = csv.writer(self.csvio)
            self.csvwr.writerow(['time', 'P1.0', 'P2.5', 'P4.0', 'P10', 'P0.5', 'P1.0', 'P2.5', 'P4.0', 'P10', "size"])
            self.csvwr.writerow(['[s]', '[µg/m³]', '[µg/m³]', '[µg/m³]', '[µg/m³]', '[#/cm³]', '[#/cm³]', '[#/cm³]', '[#/cm³]', '[#/cm³]', '[µm]'])
            self.start_measurement()
            self.mode = Mode.MEASURE
            self.running = True
            self.mthread = Thread(target=self.measure_thread)
            self.mthread.daemon = True
            self.mthread.start()
        finally:
            self.lock.release()
        return True

    def stop(self):
        if self.ser is None:
            return False
        if self.mode != Mode.MEASURE:
            return False
        self.lock.acquire()
        try:
            print('... stop measuring!')
            self.running = False
            self.mthread.join()
            self.stop_measurement()
            #self.zipf.writestr(f"measurements.csv", self.csvstr.getvalue())
            self.csvio.close()
            self.pmevents.end_measuring(self)
            self.mode = Mode.MEASURE_OFF
        finally:
            self.lock.release()
        return True

    def measure_thread(self):
        start_time = time.time()
        next_time = start_time
        while self.running:
            print(f'Wait to measure particles for {self.measure_interval} seconds ...')
            next_time = next_time + self.measure_interval
            time.sleep(next_time - time.time())
            values = self.read_values()
            print(f'Measured {len(values)} values!')
            if values is not None:
                dtime = time.time() - start_time
                self.csvwr.writerow([dtime] + list(values))

    def wait_for_bytes(self, bytes_to_read):
        in_bytes = self.ser.in_waiting
        tries = 0
        while in_bytes < bytes_to_read and tries < 10:
            time.sleep(0.1)
            in_bytes = self.ser.in_waiting
            tries = tries + 1
        return in_bytes

    def start_measurement(self):
        self.ser.write([0x7E, 0x00, 0x00, 0x02, 0x01, 0x03, 0xF9, 0x7E])
        self.ser.flush()

    def stop_measurement(self):
        self.ser.write([0x7E, 0x00, 0x01, 0x00, 0xFE, 0x7E])
        self.ser.flush()
        
    def read_values(self):
        self.ser.reset_input_buffer()
        self.ser.write([0x7E, 0x00, 0x03, 0x00, 0xFC, 0x7E])
        self.ser.flush()
        in_bytes = self.wait_for_bytes(47)
        #print("r", in_bytes)
        raw_data = self.ser.read(in_bytes)
        #print("data", raw_data)
        raw_data = reverse_byte_stuffing(raw_data)
        raw_data = trim_data(raw_data)        
        try:
            data = struct.unpack(">ffffffffff", raw_data)
        except struct.error:
            data = None
        return data     
    
    def read_product_type(self):
        self.ser.reset_input_buffer()
        self.ser.write([0x7E, 0x00, 0xD0, 0x01, 0x00, 0x2E, 0x7E])
        self.ser.flush()
        in_bytes = self.wait_for_bytes(16)
        raw_data = self.ser.read(in_bytes)
        raw_data = reverse_byte_stuffing(raw_data)
        raw_data = trim_data(raw_data)
        raw_data = raw_data[:-1]
        data = raw_data.decode("ascii")
        return data
    
    def read_serial_number(self):
        self.ser.reset_input_buffer()
        self.ser.write([0x7E, 0x00, 0xD0, 0x01, 0x03, 0x2B, 0x7E])
        self.ser.flush()
        in_bytes = self.wait_for_bytes(24)
        raw_data = self.ser.read(in_bytes)
        raw_data = reverse_byte_stuffing(raw_data)
        raw_data = trim_data(raw_data)
        raw_data = raw_data[:-1]
        data = raw_data.decode("ascii")
        return data
    
    def read_firmware_version(self):
        self.ser.reset_input_buffer()
        self.ser.write([0x7E, 0x00, 0xD1, 0x00, 0x2E, 0x7E])
        self.ser.flush()
        in_bytes = self.wait_for_bytes(14)
        raw_data = self.ser.read(in_bytes)
        raw_data = reverse_byte_stuffing(raw_data)
        raw_data = trim_data(raw_data)
        data = struct.unpack(">bbbbbbb", raw_data)
        firmware_major: int = data[0]
        firmware_minor: int = data[1]
        return firmware_major, firmware_minor
    
    def read_status_register(self):
        self.ser.reset_input_buffer()
        self.ser.write([0x7E, 0x00, 0xD2, 0x01, 0x00, 0x2C, 0x7E])
        #self.ser.flush()
        in_bytes = self.wait_for_bytes(12)
        raw_data = self.ser.read(in_bytes)
        raw_data = reverse_byte_stuffing(raw_data)
        raw_data = trim_data(raw_data)
        data = struct.unpack(">Ib", raw_data)
        register = data[0]
        return register

    def get_measure_interval(self):
        return self.measure_interval

    def set_measure_interval(self, mi):
        self.measure_interval = mi
    
if __name__ == "__main__":
    class SensorEvents(PMSensorEvents):
        def __init__(self):
            pass

        def start_measuring(self, pmsensor):
            return 'file.csv'

        def stop_measuring(self, pmsensor):
            pass

    evts = SensorEvents()
    sps = MPMSensor(evts, 2.0, '/dev/serial0')
        
    if True:
        sps.start()
        time.sleep(20)
        sps.stop()
    else:
        sps.start_measurement()
        print("start")
        for i in range(10):
            print("values", sps.read_values())
            time.sleep(2)
            print("stop")
        sps.stop_measurement()
    
    

