
import datetime
import os.path
import json
import glob

def build_base_name(name, now):
    return name + "_" + now.strftime("%Y-%m-%d_%H-%M-%S_%f")

def read_meta(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_meta(filename, meta):
    with open(filename, 'w') as f:
        json.dump(meta, f, indent = 4)

def new_meta(recdir, name, description, trigger):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    videofile = basename + ".avi"
    meta = {
        'id': basename,
        'videofile': videofile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'trigger': trigger
        }
    return meta

class Recording:
    def __init__(self, meta):
        self.meta = meta
    
    def make_video_path(self, recdir):
        videofile = self.meta['videofile']
        return os.path.join(recdir, videofile)

class Recordings:
    def __init__(self, recdir):
        self.recdir = recdir
        self.recordings = {}
        self.scan_directory()

    def scan_directory(self):
        meta_files = glob.glob(os.path.join(self.recdir, "*.json"))
        for mf in meta_files:
            print("recording: ", mf)
            meta = read_meta(mf)
            print(meta)
            self.recordings[meta['id']] = Recording(meta)

    def start_recording(self, name, description, trigger):
        return Recording(new_meta(self.recdir, name, description, trigger))

    def end_recording(self, recording):
        basename = recording.meta['id']
        jsonfile = os.path.join(self.recdir, basename + ".json")
        write_meta(jsonfile, recording.meta)
        self.recordings[basename] = recording
        return basename

    def get_video_file(self, ident):
        recording = self.recordings[ident]
        videofile = recording.meta['videofile']
        return videofile

    def get_recording(self, ident):
        recording = self.recordings[ident]
        return recording


if __name__ == "__main__":
    recs = Recordings('../recordings')
    r = recs.start_recording('test', 'desc', 'trigger')
    ide = recs.end_recording(r)
    print(recs.get_video_path(ide))
    
