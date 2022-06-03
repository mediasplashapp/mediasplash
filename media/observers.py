# observer manager
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


from cytolk import tolk
import logging
import difflib
import re


def clean(text):
    text = re.sub(r"\{.*?\}", "", text)
    text = re.sub(r"\<.*?\>", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = text.replace(r"\N", "")
    text = [line.strip() for line in text.splitlines() if line.strip()]
    return text


class ObserverManager:
    def __init__(self, player):
        self.player = player
        self.prev_value = ""

    def subtitle_observer(self, name, value):
        if not value or value.isspace():
            return
        value = self.player.sub_text_ass
        logging.debug(f"property {name} with data {value}")
        if not value:
            return

        value = clean(value)
        if not value:
            return
        if len(value) == 1:
            tolk.speak(value[0])
            self.prev_value = value
            return
        for line in difflib.ndiff(self.prev_value, value):
            if line.startswith("+ ") and line[2:].strip():
                logging.debug(f"new line {line}")
                tolk.speak(line[:2])
        self.prev_value = value

    def register_observers(self):
        self.player.observe_property("sub-text", self.subtitle_observer)
