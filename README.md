ipython_memory_usage
====================

IPython tool to report memory usage deltas for every command you type. If you are running out of RAM then use this tool to understand what's happening. It also records the time spent running each command.

This tool helps you to figure out which commands use a lot of RAM and take a long time to run, this is very useful if you're working with large numpy matrices. In addition it reports the peak memory usage whilst a command is running which might be higher (due to temporary objects) than the final RAM usage. Built on @fabianp's `memory_profiler`.

As a simple example - make 10,000,000 random numbers, report that it costs 76MB of RAM and took 0.3 seconds to execute:

    In [3]: arr=np.random.uniform(size=1E7)
    'arr=np.random.uniform(size=1E7)' used 76.2578 MiB RAM in 0.33s, peaked 0.00 MiB above current, total RAM usage 107.37 MiB

Francesc Alted has a fork with more memory delta details, see it here: https://github.com/FrancescAlted/ipython_memwatcher

Setup
=====

Supported: Python 3.4 and IPython 3.2+

Unsupported: Python 2.7 (the code used to work, it might now, I won't invest time here, you're welcome to fork it though)

Take a copy of the code or pull from https://github.com/ianozsvald/ipython_memory_usage and then:

    $ python setup.py install

If you pull it from github and you want to develop on it, it is easier to make a link in `site-packages` and develop it locally with:

    $ python setup.py develop 

To uninstall:

    $ pip uninstall ipython_memory_usage

Example usage
=============

We can measure on every line how large array operations allocate and deallocate memory:

    $ ipython
    Python 3.4.3 |Anaconda 2.3.0 (64-bit)| (default, Jun  4 2015, 15:29:08) 
    IPython 3.2.0 -- An enhanced Interactive Python.

    In [1]: import ipython_memory_usage.ipython_memory_usage as imu

    In [2]: imu.start_watching_memory()
    In [2] used 0.0469 MiB RAM in 7.32s, peaked 0.00 MiB above current, total RAM usage 56.88 MiB

    In [3]: a = np.ones(1e7)
    In [3] used 76.3750 MiB RAM in 0.14s, peaked 0.00 MiB above current, total RAM usage 133.25 MiB

    In [4]: del a
    In [4] used -76.2031 MiB RAM in 0.10s, total RAM usage 57.05 MiB


You can use `stop_watching_memory` to do stop watching and printing memory usage after each statement:

    In [5]: imu.stop_watching_memory()

    In [6]: b = np.ones(1e7)

    In [7]: b[0] * 5.0
    Out[7]: 5.0


For the beginner with numpy it can be easy to work on copies of matrices which use a large amount of RAM. The following example sets the scene and then shows an in-place low-RAM variant.

First we make a random square array and modify it twice using copies taking 2.3GB RAM:

    In [2]: a = np.random.random((1e4, 1e4))
    In [2] used 762.9531 MiB RAM in 2.21s, peaked 0.00 MiB above current, total RAM usage 812.30 MiB

    In [3]: b = a*2
    In [3] used 762.9492 MiB RAM in 0.51s, peaked 0.00 MiB above current, total RAM usage 1575.25 MiB

    In [4]: c = np.sqrt(b)
    In [4] used 762.9609 MiB RAM in 0.91s, peaked 0.00 MiB above current, total RAM usage 2338.21 MiB


Now we do the same operations but in-place on `a`, using 813MB RAM in total:

    In [2]: a = np.random.random((1e4, 1e4))
    In [2] used 762.9531 MiB RAM in 2.21s, peaked 0.00 MiB above current, total RAM usage 812.30 MiB
    In [3]: a *= 2
    In [3] used 0.0078 MiB RAM in 0.21s, peaked 0.00 MiB above current, total RAM usage 812.30 MiB
    In [4]: a = np.sqrt(a, out=a)
    In [4] used 0.0859 MiB RAM in 0.71s, peaked 0.00 MiB above current, total RAM usage 813.46 MiB

Lots of `numpy` functions have in-place operations that can assign their result back into themselves (see the `out` argument): http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs

If we make a large 1.5GB array of random integers we can `sqrt` in-place using two approaches or assign the result to a new object `b` which doubles the RAM usage:

    In [2]: a = np.random.randint(low=0, high=5, size=(10000, 20000))
    In [2] used 1525.8984 MiB RAM in 6.51s, peaked 0.00 MiB above current, total RAM usage 1575.26 MiB

    In [3]: a = np.sqrt(a)
    In [3] used 0.0430 MiB RAM in 1.93s, peaked 0.00 MiB above current, total RAM usage 1576.21 MiB

    In [4]: a = np.sqrt(a, out=a)
    In [4] used 0.1875 MiB RAM in 1.51s, peaked 0.00 MiB above current, total RAM usage 1575.44 MiB

    In [5]: b = np.sqrt(a)
    In [5] used 1525.8828 MiB RAM in 1.67s, peaked 0.00 MiB above current, total RAM usage 3101.32 MiB


We can also see the hidden temporary objects that are created _during_ the execution of a command. Below you can see that whilst `d = a * b + c` takes 3.1GB overall, it peaks at approximately 3.7GB due to the 5th temporary matrix which holds the temporary result of `a * b`.

    In [2]: a = np.ones(1e8); b = np.ones(1e8); c = np.ones(1e8)
    In [2] used 2288.8750 MiB RAM in 1.02s, peaked 0.00 MiB above current, total RAM usage 2338.06 MiB

    In [3]: d = a * b + c
    In [3] used 762.9453 MiB RAM in 0.91s, peaked 667.91 MiB above current, total RAM usage 3101.01 MiB

Knowing that a temporary is created, we can do an in-place operation instead for the same result but a lower overall RAM footprint:

    In [2]: a = np.ones(1e8); b = np.ones(1e8); c = np.ones(1e8)
    In [2] used 2288.8750 MiB RAM in 1.02s, peaked 0.00 MiB above current, total RAM usage 2338.06 MiB

    In [3]: d = a * b
    In [3] used 762.9453 MiB RAM in 0.49s, peaked 0.00 MiB above current, total RAM usage 3101.00 MiB

    In [4]: d += c
    In [4] used 0.0000 MiB RAM in 0.25s, peaked 0.00 MiB above current, total RAM usage 3101.00 MiB

For more on this example see `Tip` at http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs .

Important RAM usage note
========================

It is much easier to debug RAM situations with a fresh IPython shell. The longer you use your current shell, the more objects remain inside it and the more RAM the Operating System may have reserved. RAM is returned to the OS slowly, so you can end up with a large process with plenty of spare internal RAM (which will be allocated to your large objects), so this tool (via memory_profiler) reports 0MB RAM usage. If you get confused or don't trust the results, quit IPython and start a fresh shell, then run the fewest commands you need to understand how RAM is added to the process.


Experimental perf stat report to monitor caching
================================================

I've added experimental support for the `perf stat` tool on Linux. To use it make sure that `perf stat` runs at the command line first. Experimental support of the `cache-misses` event is enabled in this variant script (to use this `cd src/ipython_memory_usage` first):

    Python 3.4.3 |Anaconda 2.3.0 (64-bit)| (default, Jun  4 2015, 15:29:08) 
    IPython 3.2.0 -- An enhanced Interactive Python.
    In [1]: %run -i ipython_memory_usage_perf.py
    In [2]: start_watching_memory()

Here's an example that builds on the previous ones. We build a square matrix with C ordering, we also need a 1D vector of the same size:

    In [3]: ones_c = np.ones((1e4, 1e4))
    In [4]: v = np.ones(1e4)

Next we run `%timeit` using all the data in row 0. The data will reasonably fit into a cache as `v.nbytes == 80000` (80 kilobytes) and my L3 cache is 6MB. The report `perf value for cache-misses averages to 8,823/second` shows an average of 8k cache misses per seconds during this operation (followed by all the raw sampled events for reference). `%timeit` shows that this operation cost 14 microseconds per loop:

    In [5]: %timeit v * ones_c[0, :]
    run_capture_perf running: perf stat --pid 4978 --event cache-misses -I 100
    100000 loops, best of 3: 14.9 µs per loop
    In [6] used 0.1875 MiB RAM in 6.27s, peaked 0.00 MiB above current, total RAM usage 812.54 MiB
    perf value for cache-misses averages to 8,823/second, raw samples: [6273.0, 382.0, 441.0, 1103.0, 632.0, 1314.0, 180.0, 451.0, 189.0, 540.0, 159.0, 1632.0, 285.0, 949.0, 408.0, 79.0, 448.0, 1167.0, 505.0, 350.0, 79.0, 172.0, 683.0, 2185.0, 1151.0, 170.0, 716.0, 2224.0, 572.0, 1708.0, 314.0, 572.0, 21.0, 209.0, 498.0, 839.0, 955.0, 233.0, 202.0, 797.0, 88.0, 185.0, 1663.0, 450.0, 352.0, 739.0, 4413.0, 1810.0, 1852.0, 550.0, 135.0, 389.0, 334.0, 235.0, 1922.0, 658.0, 233.0, 266.0, 170.0, 2198.0, 222.0, 4702.0]

We can run the same code using alternative indexing - for column 0 we get all the row elements, this means we have to fetch the column but it is stored in row-order, so each long row goes into the cache to use just one element. Now `%timeit` reports 210 microseconds per loop which is an order of magnitude slower than before, on average we have 474k cache misses per second. This column-ordered method of indexing the data is far less cache-friendly than the previous (row-ordered) method.

    In [5]: %timeit v * ones_c[:, 0]
    run_capture_perf running: perf stat --pid 4978 --event cache-misses -I 100
    1000 loops, best of 3: 210 µs per loop
    In [5] used 0.0156 MiB RAM in 1.01s, peaked 0.00 MiB above current, total RAM usage 812.55 MiB
    perf value for cache-misses averages to 474,771/second, raw samples: [77253.0, 49168.0, 48660.0, 53147.0, 52532.0, 56546.0, 50128.0, 48890.0, 43623.0]

If the sample-gathering happens too quickly then an artifical pause is added, this means that IPython can pause for a fraction of a second which inevitably causes cache misses (as the CPU is being using and IPython is running an event loop). You can witness the baseline cache misses using `pass`:

    In [9]: pass
    run_capture_perf running: perf stat --pid 4978 --event cache-misses -I 100
    PAUSING to get perf sample for 0.3s
    In [9] used 0.0039 MiB RAM in 0.13s, peaked 0.00 MiB above current, total RAM usage 812.57 MiB
    perf value for cache-misses averages to 131,611/second, raw samples: [14111.0, 3481.0]

NOTE that this is experimental, it is only known to work on Ian's laptop using Ubuntu Linux (`perf` doesn't exist on Mac or Windows). There are some tests for the `perf` parsing code, run `nosetests perf_process.py` to confirm these work ok and validate with your own `perf` output. I'm using `perf` version 3.11.0-12. Inside `perf_process.py` the `EVENT_TYPE` can be substituted to other events like `stalled-cycles-frontend` (exit IPython and restart to make sure the run-time is good - this code is hacky!).

To trial the code run `$ python perf_process.py`, this is useful for interactive development.

Requirements
============

 * `memory_profiler` https://github.com/fabianp/memory_profiler   (`pip install memory_profiler`)
 * `perf stat` (Linux only, installed outside of Python using e.g. Synaptic, apt-get etc)

Tested on
=========

 * IPython 3.2 with Python 3.4 on Linux 64bit (2015-06)
 * IPython 2.2 with Python 2.7 on Linux 64bit (2015-06)
 * IPython 2.1 with Python 2.7 on Linux 64bit (not tested in 2015)
 * IPython 2.1 with Python 2.7 on Windows 64bit (no `perf` support, not tested in 2015)
 * IPython 2.1 with Python 2.7 on OS X 10.10 Yosemite (no `perf` support, not tested in 2015)
 * IPython 1.2 KNOWN NOT TO WORK

TO FIX
======

 * merge perf variation into the main variation as some sort of plugin (so it doesn't interfere if per not installed or available)
 * possibly try to add a counter for the size of the garbage collector, to see how many temp objects are made (disable gc first) on each command?

Problems
========

 * I can't figure out how to hook into live In prompt (at least - I can for static output, not for a dynamic output - see the code and the commented out blocks referring to `watch_memory_prompt`)
 * `python setup.py develop` will give you a sym-link from your environment back to this development folder, do this if you'd like to work on the project
