
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
