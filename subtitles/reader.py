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
import ffmpy
import os
import uuid
from . import classes


def generate_subtitles(filename, temp_dir):
    process = ffmpy.FFprobe(global_options=("-show_entries", "stream", "-print_format", "json"), inputs={filename: None})
    info = process.run()[0]
    process.destroy()
    process = None
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
            process = ffmpy.FFmpeg(inputs={filename: None}, outputs={f"{os.path.join(temp_dir.name, subtitle_file)}": ["-map", f"0:{i['index']}"]})
            process.run()
            process.destroy()
            process = None
            final.append(
                classes.Subtitle(
                    title=title,
                    language=language,
                    path=os.path.join(temp_dir.name, subtitle_file),
                    default=i["disposition"]["default"],
                )
            )
    return final
