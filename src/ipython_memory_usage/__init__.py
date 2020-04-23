"""Profile mem usage envelope of IPython commands and report interactively

Use 
In[] import ipython_memory_usage 
In[] %ipython_memory_usage_start # invoke magic-based tracking and
# %ipython_memory_usage_stop to disable
"""

from IPython.core.magic import (
    register_cell_magic, register_line_cell_magic
)

import ipython_memory_usage.ipython_memory_usage as imu


@register_line_cell_magic
def ipython_memory_usage_start(line, cell=None):
    imu.start_watching_memory()
    return 'memory profile enabled'

@register_line_cell_magic
def ipython_memory_usage_stop(line, cell=None):
    imu.stop_watching_memory()
    return 'memory profile disabled'
