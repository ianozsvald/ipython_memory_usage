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
    'a=np.random.random((1e4,1e4))' used 762.9531 MiB RAM in 2.21s, total RAM usage 812.30 MiB
    In [3]: b=a*2
    'b=a*2' used 762.9492 MiB RAM in 0.51s, total RAM usage 1575.25 MiB
    In [4]: c=np.sqrt(b)
    'c=np.sqrt(b)' used 762.9609 MiB RAM in 0.91s, total RAM usage 2338.21 MiB
    # this approach makes 3 arrays and uses 2.3GB RAM

Now we do the same operations but in-place on `a`, using 813MB RAM in total:

    In [2]: a=np.random.random((1e4,1e4))
    'a=np.random.random((1e4,1e4))' used 762.9531 MiB RAM in 2.21s, total RAM usage 812.30 MiB
    In [3]: a*=2
    'a*=2' used 0.0078 MiB RAM in 0.21s, total RAM usage 812.30 MiB
    In [4]: np.sqrt(a, a)
    'np.sqrt(a, a)' used 0.0859 MiB RAM in 0.71s, total RAM usage 813.46 MiB

Lots of `numpy` functions have in-place operations that can assign their result back into themselves (see the `out` argument): http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs

If we make a large 1.5GB array of random integers we can `sqrt` in-place using two approaches or assign the result to a new object `b` which doubles the RAM usage:

    In [2]: a=np.random.randint(low=0, high=5, size=(10000, 20000))
    'a=np.random.randint(low=0, high=5, size=(10000, 20000))' used 1525.8984 MiB RAM in 6.51s, total RAM usage 1575.26 MiB
    In [3]: a=np.sqrt(a)
    'a=np.sqrt(a)' used 0.0430 MiB RAM in 1.93s, total RAM usage 1576.21 MiB
    In [4]: np.sqrt(a, out=a)
    'np.sqrt(a, out=a)' used 0.1875 MiB RAM in 1.51s, total RAM usage 1575.44 MiB
    In [5]: b=np.sqrt(a)
    'b=np.sqrt(a)' used 1525.8828 MiB RAM in 1.67s, total RAM usage 3101.32 MiB


_NOTE_ that the method currently used looks at the memory delta between the last issued command and the end of the current command. It does not take into account any intermediate objects (which might be large) that are created and discarded before the current command completes, hence the delta estimate should be considered a lower-bound on the RAM used during the processing of the instruction (and I'd love to figure out how to get the upper-bound - see Problems below).


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
 * `Tip` at http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs notes `a*b+c` creates a temporary, the way I measure RAM misses this temporary creation so it gives a lower than expected report of how much RAM is used for intermediates. Is there a way to capture this?  Perhaps return to the thread method (as used in v0), triggered by the pre-code hook, to get the maximal memory usage sample, then show this result in addition to the final maximal memory usage (so temporaries can be reported)?  update - yes, using a thread I can see peak memory usage, now I need to capture this using the pre-code-run hook to keep a track of peak usage before final report
 * Won't report RAM usage on objects that are smaller than the Python allocated RAM, e.g. after deleting a large Py object the space left might be re-used, so the RAM usage report won't change - this will mislead newbies who won't know to start with a clean memory for RAM testing
