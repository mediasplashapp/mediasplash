import json
import subprocess
from cleaner import clean
import os


def generate_subtitles(filename, temp_dir):
    info = subprocess.getoutput(f'ffprobe -v error  -show_entries stream -print_format json "{filename}"')
    data = {}
    try:
        data = json.loads(info)
    except json.decoder.JSONDecodeError:
        return data
    final = {}
    if "streams" not in data:
        return final
    for i in data['streams']:
        if "codec_name" in i and "index" in i and i['codec_type'] == 'subtitle':
            subtitle_name = f"{i['tags']['title']}.ass"
            subprocess.call(["ffmpeg", "-i", filename, "-map", f"0:{i['index']}", f"{os.path.join(temp_dir.name, subtitle_name)}"], shell = True)
            clean(os.path.join(temp_dir.name, subtitle_name))
            final[subtitle_name] = (i['disposition']['default'], f"{os.path.join(temp_dir.name, subtitle_name)}")
    return final
