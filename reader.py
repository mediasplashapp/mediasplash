import json
import subprocess
import pyperclip
import os
def generate_subtitles(filename, temp_dir):
    info = subprocess.getoutput(f'ffprobe -v error  -show_entries stream -print_format json "{filename}"')
    pyperclip.copy(info)
    data = {}
    try:
        data = json.loads(info)
    except:
        return data
    final = {}
    if not "streams" in data:
        return final
    for i in data['streams']:
        if "codec_name" in i and "index" in i and i['codec_type'] == 'subtitle':
            subtitle_name = f"{i['tags']['title']}.srt"
            subprocess.call(["ffmpeg", "-i", filename, "-map", f"0:{i['index']}", f"{os.path.join(temp_dir.name, subtitle_name)}"])
            final[subtitle_name] = (i['disposition']['default'], f"{os.path.join(temp_dir.name, subtitle_name)}")
    return final