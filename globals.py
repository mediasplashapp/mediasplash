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

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppInfo:
    name: str = "MediaSplash"
    version: tuple = (1, 2, 1)
    data_path: str = os.path.join(os.path.expandvars("%appdata%"), "mediasplash")


info = AppInfo()
if not os.path.exists(info.data_path):
    os.mkdir(info.data_path)
