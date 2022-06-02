# observer manager
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


from functools import wraps
from cytolk import tolk
import logging


def property_log(func):
    @wraps(func)
    def logged_property(name, value):
        logging.debug(f"Observed property {name} with data {value}")
        return func(name, value)
    return logged_property

@property_log
def subtitle_observer(name, value):
    if value and value.strip():
        value = value.splitlines()
        for line in value:
            if line.strip():
                tolk.speak(line)

def register_observers(player):
    player.observe_property("sub-text", subtitle_observer)
