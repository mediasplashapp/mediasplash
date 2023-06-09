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
import sys
import os
import uuid
import logging
from . import classes

current_path = os.getcwd()
if getattr(sys, "frozen", False):
    current_path = os.path.dirname(sys.executable)


def generate_subtitles(filename, temp_dir):
    info = subprocess.getoutput(
        f'{current_path}/ffprobe -v error  -show_entries stream -print_format json "{filename}"'
    )
    logging.debug(info)
    data = {}
    final = []
    try:
        data = json.loads(info)
    except json.decoder.JSONDecodeError:
        return final
    if "streams" not in data:
        return final
    for i in data["streams"]:
        if "codec_name" in i and "index" in i and i["codec_type"] == "subtitle":
            title = ""
            language = ""
            if "title" in i["tags"]:
                title = f"{i['tags']['title']}"
            if "language" in i["tags"]:
                language = f"{i['tags']['language']}"
            subtitle_file = f"{uuid.uuid4().hex}.ass"
            res = subprocess.getoutput(
                [
                    f"{current_path}/ffmpeg",
                    "-i",
                    filename,
                    "-map",
                    f"0:{i['index']}",
                    f"{os.path.join(temp_dir.name, subtitle_file)}",
                ]
            )
            logging.debug(res)
            final.append(
                classes.Subtitle(
                    title=title,
                    language=language,
                    path=os.path.join(temp_dir.name, subtitle_file),
                    default=i["disposition"]["default"],
                )
            )
    return final
