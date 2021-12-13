import requests
import multiprocessing

class CameraNetwork:
    def __init__(self, port=5000):
        self.camera_hosts = {}
        self.port = port

    def call_hosts(self, hostaddresses, results):
        while True:
            hostaddr = hostaddresses.get()
            if hostaddr is None:
                break
            try:
                response = requests.get(f"http://{hostaddr}:{self.port}/system_state")
                json = response.json()
                print("ok", response.url)
                hostname = '<unknown>'
                if 'hostname' in json:
                    hostname = json.hostname
                results.put((hostaddr, hostname))
            except:
                print("fail", hostaddr)

    def update(self, pool_size=8):
        hostaddresses = multiprocessing.Queue()
        results = multiprocessing.Queue()

        pool = [multiprocessing.Process(target=self.call_hosts, args=(hostaddresses, results)) for i in range(pool_size)]
        for p in pool:
            p.start()

        for i in range(2, 10):
            # TODO: 192.168.1.0/24 only
            hostaddr = f"192.168.1.{i}"
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
                print("request", ip)
                response = requests.get(f"http://{ip}:{self.port}/{reqstr}", data=params, timeout=3)
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

if __name__ == "__main__":
    cn = CameraNetwork()
    cn.update() # scan the network
    print(cn.broadcast('capture_still_image', None))
    cn.broadcast('record_video', None)
    cn.broadcast('stop', None)

