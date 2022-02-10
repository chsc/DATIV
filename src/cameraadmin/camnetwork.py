import requests
import json
import multiprocessing

class CameraNetwork:
    def __init__(self, port, iptempl, iprange):
        self.camera_hosts = {}
        self.port = port
        self.iptempl = iptempl
        self.iprange = iprange
        
    def req_str(self, hostaddr, rstr):
        if self.port == 80:
            return f"http://{hostaddr}/{rstr}"
        else:
            return f"http://{hostaddr}:{self.port}/{rstr}"
        
    def call_hosts(self, hostaddresses, results):
        while True:
            hostaddr = hostaddresses.get()
            if hostaddr is None:
                break
            try:
                response = requests.get(self.req_str(hostaddr, "system_state"))
                json = response.json()
                print("ok", response.url)
                hostname = '<unknown>'
                if 'hostname' in json:
                    hostname = json.hostname
                results.put((hostaddr, hostname))
            except:
                print("fail", hostaddr)

    def update(self, pool_size = 8):
        hostaddresses = multiprocessing.Queue()
        results = multiprocessing.Queue()

        pool = [multiprocessing.Process(target=self.call_hosts, args=(hostaddresses, results)) for i in range(pool_size)]
        for p in pool:
            p.start()

        for i in range(self.iprange[0], self.iprange[1]):
            hostaddr = self.iptempl.format(i)
            hostaddresses.put(hostaddr)
        for p in pool:
            hostaddresses.put(None)

        for p in pool:
            p.join()
        
        self.camera_hosts.clear()
        while not results.empty():
            hostaddr = results.get()
            self.camera_hosts[hostaddr[0]] = hostaddr[1]

    def do_request(self, ips, reqstr, params, results):
        while True:
            ip = ips.get()
            if ip is None:
                break
            try:
                rstr = self.req_str(ip, reqstr)
                print("request", rstr)
                response = requests.get(rstr, data=params, timeout=3)
                json = response.json()
                print("ok", json)
                results.put((ip, json.result, json.status_text))
            except:
                results.put((ip, False, "Request failed"))

    def broadcast(self, reqstr, params, pool_size=8):
        ips = multiprocessing.Queue()
        results = multiprocessing.Queue()
        pool = [multiprocessing.Process(target=self.do_request, args=(ips, reqstr, params, results)) for i in range(pool_size)]
        for p in pool:
            p.start()

        for ip in self.camera_hosts:
            ips.put(ip)
        for p in pool:
            ips.put(None)

        for p in pool:
            p.join()

        ret = {}
        ok = True
        while not results.empty():
            res = results.get()
            ip = res[0]
            result = res[1]
            stext = res[2]
            ok = result and ok
            ret[ip] = (result, stext)
        return (ok, "broadcast", ret)

    def get_hosts(self):
        return self.camera_hosts

    def get_port(self):
        return self.port

    def register_camera(self, ip, hostname):
        self.camera_hosts[ip] = hostname

    def get_camera_link(self, ip):
        if self.port == 80 or self.port < 0:
            return f'http://{ip}'
        else:
            return f'http://{ip}:{self.port}'
            
    def save_cameras(self, filename):
         with open(filename, 'w') as f:
            json.dump(self.camera_hosts, f, indent = 4)
        
    def load_cameras(self, filename):
        with open(filename, 'r') as f:
            self.camera_hosts = json.load(f)

if __name__ == "__main__":
    cn = CameraNetwork()
    #cn.update() # scan the network
    #cn.load_cameras(app.config['CAMERA_HOST_FILE'])
    #print(cn.broadcast('capture_still_image', None))
    #cn.broadcast('record_video', None)
    #cn.broadcast('stop', None)

