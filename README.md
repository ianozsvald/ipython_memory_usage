ipython_memory_usage
====================

IPython tool to report memory usage deltas for every command you type.

This tool helps you to figure out which commands use a lot of RAM and take a long time to run, this is very useful if you're working with large numpy matrices.

Example usage
=============

We can measure on every line how large array operations allocate and deallocate memory:

    $ ipython --pylab
    Python 2.7.7 |Anaconda 2.0.1 (64-bit)| (default, Jun  2 2014, 12:34:02) 

    IPython 2.1.0 -- An enhanced Interactive Python.

    In [1]: %run -i  ipython_memory_usage.py
    IPython Memory usage reporter has started (exit IPython to stop using it)
    In [2]: a=np.ones(1e7)
    'a=np.ones(1e7)' used 76.2305 MiB RAM in 0.32s, total RAM usage 125.61 MiB
    In [3]: del a
    'del a' used -76.2031 MiB RAM in 0.10s, total RAM usage 49.40 MiB


Requirements
============

 * memory_profiler https://github.com/fabianp/memory_profiler 

Tested on
=========

 * IPython 2.1 with Python 2.7 on Linux 64bit

Problems
========

 * prints come after the next In[] prompt, so the display is a bit messy (hit return to get a clean new input prompt)
 * can't kill the thread after it is started so you must exit IPython to stop it
