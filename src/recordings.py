
import datetime
import os.path
import os
import json
import glob

META_FILE_EXT     = ".json"
IMAGE_FILE_EXT    = ".png"
VIDEO_FILE_EXT    = ".h264"
IMAGESEQ_FILE_EXT = ".zip"
OBJDET_FILE_EXT   = ".zip"

def build_base_name(name, now):
    return name + "_" + now.strftime("%Y-%m-%d_%H-%M-%S_%f")

def read_meta(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_meta(filename, meta):
    with open(filename, 'w') as f:
        json.dump(meta, f, indent = 4)

def new_meta_video(name, description, camera):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    metafile = basename + META_FILE_EXT
    videofile = basename + VIDEO_FILE_EXT
    meta = {
        'id': basename,
        'metafile': metafile,
        'videofile': videofile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'shutter_speed': camera.get_shutter_speed(),
        'fps': camera.get_fps(),
        'iso': camera.get_iso(),
        'brightness': camera.get_brightness(),
        'contrast': camera.get_contrast(),
        'ruler_xres': camera.get_ruler_xres(),
        'ruler_yres': camera.get_ruler_yres(),
        'passe_partout_h': camera.get_passe_partout_h(),
        'passe_partout_v': camera.get_passe_partout_v()
    }
    return meta

def new_meta_image(name, description, camera):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    metafile = basename + META_FILE_EXT
    imagefile = basename + IMAGE_FILE_EXT
    meta = {
        'id': basename,
        'metafile': metafile,
        'imagefile': imagefile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'shutter_speed': camera.get_shutter_speed(),
        'fps': camera.get_fps(),
        'iso': camera.get_iso(),
        'brightness': camera.get_brightness(),
        'contrast': camera.get_contrast(),
        'ruler_xres': camera.get_ruler_xres(),
        'ruler_yres': camera.get_ruler_yres(),
        'passe_partout_h': camera.get_passe_partout_h(),
        'passe_partout_v': camera.get_passe_partout_v()
    }
    return meta
    
def new_meta_image_sequence(name, description, camera):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    metafile = basename + META_FILE_EXT
    imageseqfile = basename + IMAGESEQ_FILE_EXT
    meta = {
        'id': basename,
        'metafile': metafile,
        'imageseqfile': imageseqfile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'shutter_speed': camera.get_shutter_speed(),
        'fps': camera.get_fps(),
        'iso': camera.get_iso(),
        'brightness': camera.get_brightness(),
        'contrast': camera.get_contrast(),
        'ruler_xres': camera.get_ruler_xres(),
        'ruler_yres': camera.get_ruler_yres(),
        'passe_partout_h': camera.get_passe_partout_h(),
        'passe_partout_v': camera.get_passe_partout_v(),
        'capture_intervall': camera.get_capture_interval()
    }
    return meta

def new_meta_objdet(name, description, camera):
    dt = datetime.datetime.now()
    basename = build_base_name(name, dt)
    metafile = basename + META_FILE_EXT
    objdetfile = basename + OBJDET_FILE_EXT
    meta = {
        'id': basename,
        'metafile': metafile,
        'objdetfile': objdetfile,
        'name': name,
        'description': description,
        'datetime': str(dt),
        'shutter_speed': camera.get_shutter_speed(),
        'fps': camera.get_fps(),
        'iso': camera.get_iso(),
        'brightness': camera.get_brightness(),
        'contrast': camera.get_contrast(),
        'ruler_xres': camera.get_ruler_xres(),
        'ruler_yres': camera.get_ruler_yres(),
        'passe_partout_h': camera.get_passe_partout_h(),
        'passe_partout_v': camera.get_passe_partout_v(),
        'capture_intervall': camera.get_capture_interval()
    }
    return meta

class Recording:
    def __init__(self, recdb, meta):
        self.recdb = recdb
        self.meta = meta

    def id(self):
        return self.meta['id']

    def is_video(self):
        return 'videofile' in self.meta

    def is_still_image(self):
        return 'imagefile' in self.meta
        
    def is_image_sequence(self):
        return 'imageseqfile' in self.meta
        
    def is_objdet(self):
        return 'objdetfile' in self.meta

    def get_file_name(self):
        if self.is_video():
            return self.meta['videofile']
        elif self.is_still_image():
            return self.meta['imagefile']
        elif self.is_image_sequence():
            return self.meta['imageseqfile']
        elif self.is_objdet():
            return self.meta['objdetfile']
        else:
            return None
            
    def get_meta_file_name(self):
        return self.meta['metafile']
    
    def make_file_path(self):
        file = self.get_file_name()
        return os.path.join(self.recdb.recdir, file)

    def make_json_path(self):
        metafile = self.get_meta_file_name()
        return os.path.join(self.recdb.recdir, metafile)

class Recordings:
    def __init__(self, recdir):
        self.recdir = recdir
        self.recordings = {}
        self.scan_directory()

    def scan_directory(self):
        meta_files = glob.glob(os.path.join(self.recdir, '*' + META_FILE_EXT))
        print("scanning directory for recordings:", self.recdir)
        for mf in meta_files:
            print(" read recording:", mf)
            meta = read_meta(mf)
            self.recordings[meta['id']] = Recording(self, meta)

    def start_recording(self, name, description, camera):
        return Recording(self, new_meta_video(name, description, camera))

    def end_recording(self, recording):
        basename = recording.meta['id']
        jsonfile = recording.make_json_path()
        write_meta(jsonfile, recording.meta)
        self.recordings[basename] = recording
        return basename
        
    def start_image_sequence(self, name, description, camera):
        return Recording(self, new_meta_image_sequence(name, description, camera))

    def end_image_sequence(self, capture):
        return self.end_recording(capture)

    def start_capture_still_image(self, name, description, camera):
        return Recording(self, new_meta_image(name, description, camera))

    def end_capture_still_image(self, capture):
        return self.end_recording(capture)
        
    def start_objdet(self, name, description, camera):
        return Recording(self, new_meta_objdet(name, description, camera))
    
    def end_objdet(self, capture):
        return self.end_recording(capture)

    def delete_recording(self, ident):
        try:
            recording = self.recordings[ident]
            os.remove(recording.make_json_path())
            os.remove(recording.make_file_path())
            del self.recordings[ident]
            return True
        except Exception as inst:
            print(inst)
            return False
            
    def delete_all_recordings(self):
        for _, r in self.recordings.items():
            os.remove(r.make_json_path())
            os.remove(r.make_file_path())
        self.recordings = {}
        return True

    def get_file(self, ident):
        try:
            recording = self.recordings[ident]
            return recording.get_file_name()
        except Exception as inst:
            print(inst)
            return None
    
    def get_meta_file(self, ident):
        try:
            recording = self.recordings[ident]
            return recording.get_meta_file_name()
        except Exception as inst:
            print(inst)
            return None
    
    def is_image_sequence(self, ident):
        try:
            recording = self.recordings[ident]
            return recording.is_image_sequence()
        except Exception:
            return False

    def get_recording(self, ident):
        try:
            return self.recordings[ident]
        except Exception as inst:
            print(inst)
            return None
        

if __name__ == "__main__":
    recs = Recordings('../recordings')
    r = recs.start_recording('test', 'desc', 'trigger', None)
    ide = recs.end_recording(r)
    print(r.make_file_path())
    
