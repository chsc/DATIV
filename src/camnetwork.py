import requests
import multiprocessing

class CameraNetwork:
    def __init__(self, port=5000):
        self.camera_hosts = []
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
            self.camera_hosts.append(hostaddr)

    def call_request(self, ips, reqstr, params):
        while True:
            ip = ips.get()
            if ip is None:
                break
            try:
                response = requests.get(f"http://{ip}:{self.port}/{reqstr}", data=params)
                json = response.json()
                print("ok", json)
                #results.put((hostaddr, hostname))
            except:
                print("fail", ip)

    def broadcast(self, reqstr, params, pool_size=8):
        ips = multiprocessing.Queue()
        pool = [multiprocessing.Process(target=self.call_request, args=(ips, reqstr, params)) for i in range(pool_size)]
        for p in pool:
            p.start()

        for h in self.camera_hosts:
            ip = h[0]
            ips.put(ip)
        for p in pool:
            ips.put(None)

        for p in pool:
            p.join()

    def get_hosts(self):
        return self.camera_hosts

    def get_port(self):
        return self.port

if __name__ == "__main__":
    cn = CameraNetwork()
    cn.update() # scan the network
    cn.broadcast('capture_still_image', None)
    cn.broadcast('record_video', None)
    cn.broadcast('stop', None)

