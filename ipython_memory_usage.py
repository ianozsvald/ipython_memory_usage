from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import os
import time
import memory_profiler

# To run: %run -i memory_watcher.py

# keep a global accounting for the last known memory usage
# which is the reference point for the memory delta calculation
previous_call_memory_usage = memory_profiler.memory_usage()[0]
t1 = time.time() # will be set to current time later


def watch_memory():
    import time
    # bring in the global memory usage value from the previous iteration
    global previous_call_memory_usage
    nbr_commands = len(In)
    new_memory_usage = memory_profiler.memory_usage()[0]
    memory_delta = new_memory_usage - previous_call_memory_usage
    # calculate time delta using global t1 (from the pre-run event) and current
    # time
    time_delta_secs = time.time() - t1
    cmd = In[nbr_commands-1]
    # convert the results into a pretty string
    output_template = "'{cmd}' used {memory_delta:0.4f} MiB RAM in {time_delta:0.2f}s, total RAM usage {memory_usage:0.2f} MiB"
    output = output_template.format(time_delta=time_delta_secs,
                                    cmd=cmd,
                                    memory_delta=memory_delta,
                                    memory_usage=new_memory_usage)
    print(str(output))
    previous_call_memory_usage = new_memory_usage


def pre_run_cell():
    """Capture current time before we execute the current command"""
    import time
    global t1
    t1 = time.time()


if __name__ == "__main__":
    if 'In' not in dir():
        script_name = os.path.split(__file__)[1]
        raise ValueError("You must run this from IPython interactively using e.g. '%run -i {}'".format(script_name))

    ip = get_ipython()
    # http://ipython.org/ipython-doc/dev/api/generated/IPython.core.events.html
    ip.events.register("post_run_cell", watch_memory)
    ip.events.register("pre_run_cell", pre_run_cell)
