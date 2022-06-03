"""
    mediasplash, A simple media player with screen reader subtitle support.
    Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import subprocess
import os
import uuid
import logging


def generate_subtitles(filename, temp_dir):
    info = subprocess.getoutput(
        f'ffprobe -v error  -show_entries stream -print_format json "{filename}"'
    )
    logging.debug(info)
    data = {}
    try:
        data = json.loads(info)
    except json.decoder.JSONDecodeError:
        return data
    final = {}
    if "streams" not in data:
        return final
    for i in data["streams"]:
        if "codec_name" in i and "index" in i and i["codec_type"] == "subtitle":

            if "title" in i["tags"]:
                subtitle_name = f"{i['tags']['title']}.ass"
            else:
                subtitle_name = f"{i['tags']['language']}.ass"

            subtitle_file = f"{uuid.uuid4().hex}.ass"
            res = subprocess.getoutput(
                [
                    "ffmpeg",
                    "-i",
                    filename,
                    "-map",
                    f"0:{i['index']}",
                    f"{os.path.join(temp_dir.name, subtitle_file)}",
                ]
            )
            logging.debug(res)
            final[subtitle_name.replace(".ass", "")] = (
                i["disposition"]["default"],
                f"{os.path.join(temp_dir.name, subtitle_file)}",
            )
    return final
