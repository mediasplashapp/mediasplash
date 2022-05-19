import json
import subprocess
import os
import uuid
import logging


def generate_subtitles(filename, temp_dir):
    info = subprocess.getoutput(f'ffprobe -v error  -show_entries stream -print_format json "{filename}"')
    logging.debug(info)
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
            subtitle_file = f"{uuid.uuid4().hex}.ass"
            res = subprocess.getoutput(["ffmpeg", "-i", filename, "-map", f"0:{i['index']}", f"{os.path.join(temp_dir.name, subtitle_file)}"])
            logging.debug(res)
            final[subtitle_name.replace(".ass", "")] = (i['disposition']['default'], f"{os.path.join(temp_dir.name, subtitle_file)}")
    return final
