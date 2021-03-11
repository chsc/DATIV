
import datetime
import os.path
import os
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

def new_meta(recdir, name, description, trigger, iso=100, brightness=50, contrast=0):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    metafile = basename + ".json"
    videofile = basename + ".mp4"
    meta = {
        'id': basename,
        'metafile': metafile,
        'videofile': videofile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'trigger': trigger,
        'iso': iso,
        "brightness": brightness,
        "contrast": contrast
    }
    return meta

class Recording:
    def __init__(self, meta):
        self.meta = meta
    
    def make_video_path(self, recdir):
        videofile = self.meta['videofile']
        return os.path.join(recdir, videofile)

    def make_json_path(self, recdir):
        metafile = self.meta['metafile']
        return os.path.join(recdir, metafile)

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

    def start_recording(self, name, description, trigger, iso, brightness, contrast):
        return Recording(new_meta(self.recdir, name, description, trigger, iso, brightness, contrast))

    def end_recording(self, recording):
        basename = recording.meta['id']
        jsonfile = recording.make_json_path(self.recdir)
        write_meta(jsonfile, recording.meta)
        self.recordings[basename] = recording
        return basename

    def delete_recording(self, ident):
        try:
            recording = self.recordings[ident]
            os.remove(recording.make_json_path(self.recdir))
            os.remove(recording.make_video_path(self.recdir))
            del self.recordings[ident]
            return True
        except Exception as inst:
            print(inst)
            return False

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
    
