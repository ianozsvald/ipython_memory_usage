#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Profile mem usage envelope of IPython commands and report interactively"""
import time
import memory_profiler
from IPython import get_ipython
import psutil  # ADDED

# __version__ = 1.1  # set to desired value.
# Disabled for now, I'll use pyproject.toml for this
# we could use:
# from importlib.metadata import version
# version("ipython_memory_usage") -> "1.2"
# I've moved the above to __init__.py

# To run: %run -i ipython_memory_usage.py
# but there will be no output

# keep a global accounting for the last known memory usage
# which is the reference point for the memory delta calculation
previous_call_memory_usage = memory_profiler.memory_usage()[0]
t1 = time.time()  # will be set to current time later
keep_watching = True
peak_memory_usage = -1
cpu_utilisation_list = []
watching_memory = True
input_cells = get_ipython().user_ns["In"]


def start_watching_memory():
    """Register memory profiling tools to IPython instance."""
    global watching_memory

    # Just in case start is called more than once, stop watching. Hence unregister events
    stop_watching_memory()

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


def watch_memory(execution_result):
    """Prints the memory usage if watching the memory"""
    # print(type(execution_result)) # <class 'IPython.core.interactiveshell.ExecutionResult'>
    # bring in the global memory usage value from the previous iteration
    global previous_call_memory_usage, peak_memory_usage, keep_watching, watching_memory, input_cells
    new_memory_usage = memory_profiler.memory_usage()[0]
    memory_delta = new_memory_usage - previous_call_memory_usage
    keep_watching = False
    peaked_memory_usage = max(0, peak_memory_usage - new_memory_usage)
    # calculate time delta using global t1 (from the pre-run event) and current
    # time
    time_delta_secs = time.time() - t1
    num_commands = len(input_cells) - 1
    cmd = "In [{}]".format(num_commands)

    # summarise cpu utililisation
    cpu_means = []
    cpu_max = 0
    cpu_mean = 0
    for row in cpu_utilisation_list:
        mean = sum(row) / len(row)
        cpu_means.append(mean)
        cpu_max = max(cpu_max, max(row))
    if len(cpu_utilisation_list) > 0:
        cpu_mean = sum(cpu_means) / len(cpu_means)

    # convert the results into a pretty string
    output_template = (
        "{cmd} used {memory_delta:0.1f} MiB RAM in "
        "{time_delta:0.2f}s (system mean cpu {cpu_mean:0.0f}%, single max cpu {cpu_max:0.0f}%), peaked {peaked_memory_usage:0.1f} "
        "MiB above final usage, current RAM usage now "
        "{memory_usage:0.1f} MiB"
    )
    output = output_template.format(
        time_delta=time_delta_secs,
        cmd=cmd,
        memory_delta=memory_delta,
        peaked_memory_usage=peaked_memory_usage,
        memory_usage=new_memory_usage,
        cpu_mean=cpu_mean,
        cpu_max=cpu_max,
    )
    if watching_memory:
        print(str(output))
    previous_call_memory_usage = new_memory_usage


def during_execution_memory_sampler():
    """Thread to sample memory usage"""
    import time
    import memory_profiler

    global keep_watching, peak_memory_usage, cpu_utilisation_list
    peak_memory_usage = -1
    cpu_utilisation_list = []
    psutil.cpu_percent()  # must call it once to clear the built-in history
    keep_watching = True

    n = 0
    WAIT_BETWEEN_SAMPLES_SECS = 0.001
    MAX_ITERATIONS = 60.0 / WAIT_BETWEEN_SAMPLES_SECS
    while True:
        # get memory details
        mem_usage = memory_profiler.memory_usage()[0]
        peak_memory_usage = max(mem_usage, peak_memory_usage)

        # get cpu usage details
        this_cpu_utilisation = psutil.cpu_percent(
            percpu=True
        )  # get cpu utilisation per cpu
        cpu_utilisation_list.append(this_cpu_utilisation)

        time.sleep(WAIT_BETWEEN_SAMPLES_SECS)
        if not keep_watching or n > MAX_ITERATIONS:
            # exit if we've been told our command has finished or if it has run
            # for more than a sane amount of time (e.g. maybe something crashed
            # and we don't want this to carry on running)
            if n > MAX_ITERATIONS:
                print(
                    "{} SOMETHING WEIRD HAPPENED AND THIS RAN FOR TOO LONG, THIS THREAD IS KILLING ITSELF".format(
                        __file__
                    )
                )
            break
        n += 1


def pre_run_cell(execution_result):
    """Capture current time before we execute the current command"""
    import time

    global t1
    t1 = time.time()

    # start a thread that samples RAM usage until the current command finishes
    import threading

    ipython_memory_usage_thread = threading.Thread(
        target=during_execution_memory_sampler
    )
    ipython_memory_usage_thread.daemon = True
    ipython_memory_usage_thread.start()


def expensive_fn():
    """test fn to make the machine do some work"""
    # import math
    for _ in range(10):
        nbr = [n for n in range(1_000_000)]
        max_nbr = max(nbr)
    return max_nbr


if __name__ == "__main__":
    # if we e.g. %run -i cell_profiler.py from IPython
    start_watching_memory()
