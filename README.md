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


The reports can help us to optimise our code. Here's an example of a less optimal approach to masking:

    In [2]: a=np.random.random((1e5,1e3))
    'a=np.random.random((1e5,1e3))' used 762.7930 MiB RAM in 0.21s, total RAM usage 812.18 MiB
    In [3]: b=a>0.5
    'b=a>0.5' used 95.3789 MiB RAM in 0.43s, total RAM usage 907.55 MiB
    In [4]: c=a[b]
    'c=a[b]' used 381.5547 MiB RAM in 0.21s, total RAM usage 1289.11 MiB

The above block makes a random array, creates a mask, then uses the mask to select a new `c`, in total 1.2GB is used.

Instead in the following we can see that avoiding `b` saves us 100MB _and_ allows `c` to be a _view_ onto `a` which avoids creating a new matrix, in total only 900MB is used:

    In [2]: a=np.random.random((1e5,1e3))
    'a=np.random.random((1e5,1e3))' used 762.7930 MiB RAM in 0.21s, total RAM usage 812.18 MiB
    In [3]: c=a>0.5
    'c=a>0.5' used 95.3789 MiB RAM in 0.43s, total RAM usage 907.55 MiB







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
