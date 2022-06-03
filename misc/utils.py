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

import os
from pathlib import Path
from enum import Enum


supported_subtitles = (".ass", ".ssa", ".srt")


def generate_track_info(origin, type):
    final = []
    for i in origin:
        if not "type" in i:
            continue
        if i["type"] == type:
            if not "title" in i or i["title"] == "":
                final.append(i["lang"])
            else:
                final.append(i["title"])
    return final


def check_for_similar_subtitles(dir, file):
    p = Path(os.path.join(dir, file))
    final = {}
    filename = p.stem
    for i in supported_subtitles:
        if p.with_suffix(i).exists():
            final[filename] = (0, f"{os.path.join(dir, filename)}{i}")
    return final


def get_subtitle_tuple(sub):
    return (sub.start, sub.end, sub.text)


class MediaState(Enum):
    neverPlayed = 0
    stopped = 1
    paused = 2
    playing = 3
