# observer manager
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


from cytolk import tolk
import logging


class ObserverManager:
    def __init__(self, player):
        self.player = player

    def subtitle_observer(self, name, value):
        logging.debug(f"property {name} with data {value}")
        if value:
            value = value.splitlines()
            current_string = ""
            for line in value:
                current_string += line
                if line.endswith(" "):
                    continue
                tolk.speak(current_string)
                current_string = ""

    def register_observers(self):
        self.player.observe_property("sub-text", self.subtitle_observer)
