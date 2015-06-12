#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Use Linux perf tool to interrogate the CPU's performance counters"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import os
import time
import memory_profiler
from IPython import get_ipython
import perf_process

# keep a global accounting for the last known memory usage
# which is the reference point for the memory delta calculation
previous_call_memory_usage = memory_profiler.memory_usage()[0]
t1 = time.time() # will be set to current time later
keep_watching = True
peak_memory_usage = -1
perf_proc = None

watching_memory = True
input_cells = get_ipython().user_ns['In']


def start_watching_memory():
    """Register memory profiling tools to IPython instance."""
    global watching_memory
    watching_memory = True
    ip = get_ipython()
    ip.events.register("post_run_cell", watch_memory)
    ip.events.register("pre_run_cell", pre_run_cell)


def stop_watching_memory():
    """Unregister memory profiling tools from IPython instance."""
    global watching_memory
    watching_memory = False
    ip = get_ipython()
    try:
        ip.events.unregister("post_run_cell", watch_memory)
    except ValueError:
        pass
    try:
        ip.events.unregister("pre_run_cell", pre_run_cell)
    except ValueError:
        pass

def watch_memory():
    import time
    # bring in the global memory usage value from the previous iteration
    global previous_call_memory_usage, peak_memory_usage, keep_watching, perf_proc, \
           watching_memory, input_cells
    #nbr_commands = len(In)
    new_memory_usage = memory_profiler.memory_usage()[0]
    memory_delta = new_memory_usage - previous_call_memory_usage
    keep_watching = False
    peaked_memory_usage = max(0, peak_memory_usage - new_memory_usage)
    # calculate time delta using global t1 (from the pre-run event) and current
    # time
    time_delta_secs = time.time() - t1
    perf_values = []
    if perf_proc:
        # pause if necessary to attempt to make sure we get a sample from perf...
        # as the 100ms min sample time and flushing oddness means I don't get a
        # sample very quickly for short-running tasks
        MIN_TIME_TO_GET_PERF_SAMPLE = 0.2
        if time_delta_secs < MIN_TIME_TO_GET_PERF_SAMPLE:
            print("PAUSING to get perf sample for {}s".format(MIN_TIME_TO_GET_PERF_SAMPLE))
            time.sleep(MIN_TIME_TO_GET_PERF_SAMPLE)  # pause until at least 0.1s has passed
        # if we have a valid perf running then capture that information
        perf_values = perf_process.finish_perf(perf_proc)
    
    cmd = ""  #In[nbr_commands-1]
    # convert the results into a pretty string
    #output_template = "'{cmd}' used {memory_delta:0.4f} MiB RAM in {time_delta:0.2f}s, peaked {peaked_memory_usage:0.2f} MiB above current, total RAM usage {memory_usage:0.2f} MiB"
    output_template = "Used {memory_delta:0.4f} MiB RAM in {time_delta:0.2f}s, peaked {peaked_memory_usage:0.2f} MiB above current, total RAM usage {memory_usage:0.2f} MiB"
    output = output_template.format(time_delta=time_delta_secs,
                                    cmd=cmd,
                                    memory_delta=memory_delta,
                                    peaked_memory_usage=peaked_memory_usage,
                                    memory_usage=new_memory_usage)
    print(str(output))
    if perf_values:
        perf_average = int(sum(perf_values) / float(time_delta_secs))
        #print("perf value for {} averages to {:,}/second, raw samples:".format(perf_process.EVENT_TYPE, perf_average), perf_values)
        print("perf value for {} averages to {:,}/second".format(perf_process.EVENT_TYPE, perf_average))
    else:
        print("perf - no results to report, possibly the collection time was too short?")
    previous_call_memory_usage = new_memory_usage


def during_execution_memory_sampler():
    import time
    import memory_profiler
    global keep_watching, peak_memory_usage
    peak_memory_usage = -1
    keep_watching = True

    n = 0
    WAIT_BETWEEN_SAMPLES_SECS = 0.001
    MAX_ITERATIONS = 60.0 / WAIT_BETWEEN_SAMPLES_SECS
    while True:
        mem_usage = memory_profiler.memory_usage()[0]
        peak_memory_usage = max(mem_usage, peak_memory_usage)
        time.sleep(WAIT_BETWEEN_SAMPLES_SECS)
        if not keep_watching or n > MAX_ITERATIONS:
            # exit if we've been told our command has finished or if it has run
            # for more than a sane amount of time (e.g. maybe something crashed
            # and we don't want this to carry on running)
            if n > MAX_ITERATIONS:
                print("{} SOMETHING WEIRD HAPPENED AND THIS RAN FOR TOO LONG, THIS THREAD IS KILLING ITSELF".format(__file__))
            break
        n += 1


def pre_run_cell():
    """Capture current time before we execute the current command"""
    import time
    import os
    global perf_proc, t1
    # t1 records the start time of this execution cycle
    t1 = time.time()

    # start a thread that samples RAM usage until the current command finishes
    import threading
    ipython_memory_usage_thread = threading.Thread(target=during_execution_memory_sampler)
    ipython_memory_usage_thread.daemon = True
    ipython_memory_usage_thread.start()

    pid = os.getpid()
    perf_proc = perf_process.run_capture_perf(pid)