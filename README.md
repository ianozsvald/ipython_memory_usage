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
    In [2]: a=np.ones(1e7)
    'a=np.ones(1e7)' used 76.2305 MiB RAM in 0.32s, total RAM usage 125.61 MiB
    In [3]: del a
    'del a' used -76.2031 MiB RAM in 0.10s, total RAM usage 49.40 MiB

For the beginner with numpy it can be easy to work on copies of matrices which use a large amount of RAM. The following example sets the scene and then shows an in-place low-RAM variant.

First we make a random square array and modify it twice using copies taking 2.3GB RAM:

    In [2]: a=np.random.random((1e4,1e4))
    'a=np.random.random((1e4,1e4))' used 762.9531 MiB RAM in 0.21s, total RAM usage 812.30 MiB
    In [3]: b=a*2
    'b=a*2' used 762.9492 MiB RAM in 0.21s, total RAM usage 1575.25 MiB
    In [4]: c=np.sqrt(b)
    'c=np.sqrt(b)' used 762.9609 MiB RAM in 0.21s, total RAM usage 2338.21 MiB
    # this approach makes 3 arrays and uses 2.3GB RAM

Now we do the same operations but in-place on `a`, using 813MB RAM in total:

    In [2]: a=np.random.random((1e4,1e4))
    'a=np.random.random((1e4,1e4))' used 762.9531 MiB RAM in 0.21s, total RAM usage 812.30 MiB
    In [3]: a*=2
    'a*=2' used 0.0078 MiB RAM in 0.21s, total RAM usage 812.30 MiB
    In [4]: np.sqrt(a, a)
    'np.sqrt(a, a)' used 0.0859 MiB RAM in 0.21s, total RAM usage 813.46 MiB


Requirements
============

 * memory_profiler https://github.com/fabianp/memory_profiler 

Tested on
=========

 * IPython 2.1 with Python 2.7 on Linux 64bit
 * IPython 2.1 with Python 2.7 on Windows 64bit

Problems
========

 * prints come after the next In[] prompt, so the display is a bit messy (hit return to get a clean new input prompt)
 * I can't figure out how to hook into live In prompt (at least - I can for static output, not for a dynamic output - see the code and the commented out blocks referring to `watch_memory_prompt`)
 * I haven't figured out how to disable the tool - probably an `argparse` with an option to disable would be a nice start
 * Needs a `setup.py` to install it
