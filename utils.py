import os
from pathlib import Path
from cleaner import clean
from enum import Enum

supported_subtitles = (".ass", ".ssa", ".srt")


def check_for_similar_subtitles(dir, file):
    p = Path(os.path.join(dir, file))
    final = {}
    filename = p.stem
    for i in supported_subtitles:
        if p.with_suffix(i).exists():
            final[filename] = (0, f"{os.path.join(dir, filename)}{i}")
            clean(f"{os.path.join(dir, filename)}{i}")
    return final


def get_subtitle_tuple(sub):
    return (sub.start, sub.end, sub.text)


class MediaState(Enum):
    neverPlayed = 0
    stopped = 1
    paused = 2
    playing = 3
