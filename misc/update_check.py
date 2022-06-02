# update_check
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


import requests
from globals import info


URL = "https://api.github.com/repos/mediasplashapp/mediasplash/releases/latest"


def check():
    with requests.get(URL) as res:
        if res.ok:
            data = res.json()
            ver = data["tag_name"].lower().strip("v")
            ver = tuple([int(v) for v in ver.split(".")])
            for i, j in zip(ver, info.version):
                if i > j:
                    return [str(i) for i in ver]
            return False
        res.raise_for_status()
