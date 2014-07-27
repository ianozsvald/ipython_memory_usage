ipython_memory_usage
====================

IPython tool to report memory usage deltas for every command you type. If you are running out of RAM then use this tool to understand what's happening.

This tool helps you to figure out which commands use a lot of RAM and take a long time to run, this is very useful if you're working with large numpy matrices. In addition it reports the peak memory usage whilst a command is running which might be higher (due to temporary objects) than the final RAM usage. Built on @fabianp's `memory_profiler`.

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


We can also see the hidden temporary objects that are created _during_ the execution of a command. Below you can see that whilst `d=a*b+c` takes 3.1GB overall, it peaks at approximately 3.7GB due to the 5th temporary matrix which holds the temporary result of `a*b`.

    In [2]: a=np.ones(1e8); b=np.ones(1e8); c=np.ones(1e8)
    'a=np.ones(1e8); b=np.ones(1e8); c=np.ones(1e8)' used 2288.8750 MiB RAM in 1.02s, peaked 0.00 MiB above current, total RAM usage 2338.06 MiB
    In [3]: d=a*b+c
    'd=a*b+c' used 762.9453 MiB RAM in 0.91s, peaked 667.91 MiB above current, total RAM usage 3101.01 MiB

Knowing that a temporary is created, we can do an in-place operation instead for the same result but a lower overall RAM footprint:

    In [2]: a=np.ones(1e8); b=np.ones(1e8); c=np.ones(1e8)
    'a=np.ones(1e8); b=np.ones(1e8); c=np.ones(1e8)' used 2288.8750 MiB RAM in 1.02s, peaked 0.00 MiB above current, total RAM usage 2338.06 MiB
    In [3]: d=a*b
    'd=a*b' used 762.9453 MiB RAM in 0.49s, peaked 0.00 MiB above current, total RAM usage 3101.00 MiB
    In [4]: d+=c
    'd+=c' used 0.0000 MiB RAM in 0.25s, peaked 0.00 MiB above current, total RAM usage 3101.00 MiB

For more on this example see `Tip` at http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs .

Important RAM usage note
========================

It is much easier to debug RAM situations with a fresh IPython shell. The longer you use your current shell, the more objects remain inside it and the more RAM the Operating System may have reserved. RAM is returned to the OS slowly, so you can end up with a large process with plenty of spare internal RAM (which will be allocated to your large objects), so this tool (via memory_profiler) reports 0MB RAM usage. If you get confused or don't trust the results, quit IPython and start a fresh shell, then run the fewest commands you need to understand how RAM is added to the process.


Experimental perf stat report to monitor caching
================================================

I've added experimental support for the `perf stat` tool on Linux. To use it make sure that `perf stat` runs at the command line first. Experimental support of the `cache-misses` event is enabled in this variant script:

    %run -i ipython_memory_usage_perf.py

Here's an example that builds on the previous ones. We build a square matrix with C ordering, we also need a 1D vector of the same size:

    In [2]: ones_c = np.ones((1e4,1e4))
    In [3]: v = np.ones(1e4)

Next we run `%timeit` using all the data in row 0. The data will reasonably fit into a cache. The report `perf sum over cache-misses events: 18264.0` shows a total of 18k cache misses during this operation (followed by all the raw sampled events for reference). `%timeit` ran 10,000 loops so we divide 18k/10k and we have an average of 1.8 cache misses per loop (and `%timeit` reports 66 microseconds per loop).

    In [7]: %timeit v*ones_c[0,:]
    run_capture_perf running: perf stat --pid 4633 --event cache-misses -I 100
    10000 loops, best of 3: 66.6 µs per loop
    'get_ipython().magic(u'timeit v*ones_c[0,:]')' used 0.1953 MiB RAM in 3.01s, peaked 0.00 MiB above current, total RAM usage 1575.74 MiB
    perf sum over cache-misses events: 18264.0 [9709.0, 304.0, 290.0, 93.0, 422.0, 1369.0, 115.0, 877.0, 189.0, 49.0, 544.0, 156.0, 147.0, 27.0, 118.0, 55.0, 528.0, 1200.0, 97.0, 80.0, 395.0, 47.0, 860.0, 48.0, 440.0, 69.0, 36.0]
    In [10]: 18264.0/10000
    run_capture_perf running: perf stat --pid 4633 --event cache-misses -I 100
    Out[10]: 1.8264

We can run the same code using alternative indexing - for column 0 we get all the row elements, this means we have to fetch the column but it is stored in row-order, so each long row goes into the cache to use just one element. `%timeit` reports 811 microseconds per loop - an order of magnitude slower than the previous form. The sum of cache-misses is 266276, over 1,000 loops we have 266 cache misses per loop. We can see that this approach is significantly less cache-friendly than the previous approach.

    In [8]: %timeit v*ones_c[:,0]
    run_capture_perf running: perf stat --pid 4633 --event cache-misses -I 100
    1000 loops, best of 3: 811 µs per loop
    'get_ipython().magic(u'timeit v*ones_c[:,0]')' used 0.0000 MiB RAM in 3.60s, peaked 0.00 MiB above current, total RAM usage 1575.74 MiB
    perf sum over cache-misses events: 266276.0 [16213.0, 14394.0, 7108.0, 7134.0, 11397.0, 12103.0, 6202.0, 5972.0, 6937.0, 7469.0, 11338.0, 5571.0, 5556.0, 6159.0, 7199.0, 9346.0, 9343.0, 5759.0, 6796.0, 6766.0, 6990.0, 7411.0, 10099.0, 6671.0, 7962.0, 9144.0, 6244.0, 5958.0, 12138.0, 7234.0, 6867.0, 5251.0, 5545.0]

    In [9]: 266276.0/1000
    run_capture_perf running: perf stat --pid 4633 --event cache-misses -I 100
    Out[9]: 266.276

NOTE that this is experimental, it is only known to work on Ian's laptop using Ubuntu Linux. There are some tests for the `perf` parsing code, run `nosetests perf_process.py` to confirm these work ok and validate with your own `perf` output. I'm using `perf` version 3.11.0-12. Inside `perf_process.py` the `EVENT_TYPE` can be substituted to other events like `stalled-cycles-frontend` (exit IPython and restart to make sure the run-time is good - this code is hacky!).

To trial the code run `$ python perf_process.py`, this is useful for interactive development.

Requirements
============

 * memory_profiler https://github.com/fabianp/memory_profiler 

Tested on
=========

 * IPython 2.1 with Python 2.7 on Linux 64bit
 * IPython 2.1 with Python 2.7 on Windows 64bit

Problems
========

 * I can't figure out how to hook into live In prompt (at least - I can for static output, not for a dynamic output - see the code and the commented out blocks referring to `watch_memory_prompt`)
 * I haven't figured out how to disable the tool - probably an `argparse` with an option to disable would be a nice start which disables the hooks?
 * Needs a `setup.py` to install it
