import json
import subprocess


test = subprocess.getoutput("ffprobe -v error  -show_entries stream -print_format json test.mkv")
with open("test.json", "w") as f:
    f.write(test)
