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

import glob, os, csv
from detector import detect_image, detect_video, transcode, count_frames


with open("frames.txt", "w") as csvf:
	writer = csv.writer(csvf)
	writer.writerow(["File", "Test", "Res", "SM", "FPS", "Frames"])
	for f in sorted(glob.glob("*.h264")):
		print("file", f)
		sf = f.split("_")
		n = sf[0]
		res = sf[1]
		sm = sf[2][2:]
		fps = sf[3][:2]
		#frms = count_frames(f)
		frms = transcode(f, f + ".mp4", int(fps))
		print(" frames:", frms)
		writer.writerow([f, n, res, sm, fps, frms])
