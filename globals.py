from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppInfo:
    name: str = "MediaSlash"
    version: float = 1.0
    data_path: str = os.path.join(os.path.expandvars("%appdata%"), "mediaslash")


info = AppInfo()
if not os.path.exists(info.data_path):
    os.mkdir(info.data_path)
