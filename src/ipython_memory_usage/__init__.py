"""Profile mem usage envelope of IPython commands and report interactively

Use 
In[] %load_ext ipython_memory_usage
In[] %imu_start # invoke magic-based tracking and
# %imu_stop to disable
"""

import ipython_memory_usage.ipython_memory_usage as imu

from importlib.metadata import version
__version__ = version("ipython_memory_usage") # -> e.g. "1.2"


#from IPython.core.magic import (
#    register_cell_magic, register_line_cell_magic
#)

#@register_line_cell_magic
#def ipython_memory_usage_start(line, cell=None):
#    imu.start_watching_memory()
#    return 'memory profile enabled'

#@register_line_cell_magic
#def ipython_memory_usage_stop(line, cell=None):
#    imu.stop_watching_memory()
#    return 'memory profile disabled'

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)

# The class MUST call this class decorator at creation time
# https://ipython.readthedocs.io/en/stable/config/custommagics.html
@magics_class
class IPythonMemoryUsageMagics(Magics):

    @line_magic
    def lmagic(self, line):
        "my line magic"
        print("Full access to the main IPython object:", self.shell)
        print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
        return line

    #@cell_magic
    #def cmagic(self, line, cell):
    #    "my cell magic"
    #    return line, cell

    @line_magic
    def imu_start(self, line):
        """Start CPU & memory profiling for IPython Memory Usage"""
        imu.start_watching_memory()
        return "IPython Memory Usage started"

    @line_magic
    def imu_stop(self, line):
        """End profiling for IPython Memory Usage"""
        imu.stop_watching_memory()
        return "IPython Memory Usage stopped"


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    print("Enabling IPython Memory Usage, use %imu_start to begin, %imu_stop to end")
    ipython.register_magics(IPythonMemoryUsageMagics)
