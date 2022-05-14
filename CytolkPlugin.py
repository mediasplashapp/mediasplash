import glob
from pathlib import Path
import shutil

from nuitka.plugins.PluginBase import NuitkaPluginBase


def get_libraries(module):
    """Returns a  list of the libraries needed by cytolk"""
    cytolk_dir = module.getCompileTimeDirectory()
    return list(glob.glob(f'{cytolk_dir}/*.dll'))

class CytolkPlugin(NuitkaPluginBase):
    plugin_name = "cytolk"
    plugin_desc = "provides cytolk support"
    
    def __init__(self):
        self.copied_cytolk = False    

    def considerExtraDlls(self, dist_dir, module):
        libs = get_libraries(module)
        name = module.getFullName()
        # to avoid copying files twice
        if self.copied_cytolk == False and name == "cytolk":
            for lib in libs:
                shutil.copy(lib, str(Path(dist_dir)))
                self.info(f'copied {lib}')
            self.copied_cytolk = True
        return ()

