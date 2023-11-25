ipython_memory_usage
====================

*CURRENT SITUATION - Ian is updating this, so this README is probably out of date, only this first section is actually correct as of 2023-11-24*

IPython tool to report memory usage deltas for every command you type. If you are running out of RAM then use this tool to understand what's happening. It also records the time spent running each command.

This tool helps you to figure out which commands use a lot of RAM and take a long time to run, this is very useful if you're working with large numpy matrices. In addition it reports the peak memory usage whilst a command is running which might be higher (due to temporary objects) than the final RAM usage. Built on @fabianp's `memory_profiler`.

As a simple example - make 10,000,000,000 "ones", report that it costs 57GB of RAM and took 35 seconds to execute, with 1 CPU at 100% for at least some of the time and the overall CPU usage being 10% (as only 1 core was running):

```
$ ipython
...
In [1]: %load_ext ipython_memory_usage
Enabling IPython Memory Usage, use %imu_start to begin, %imu_stop to end

In [2]: %imu_start
Out[2]: 'IPython Memory Usage started'
In [2] used 1.0 MiB RAM in 8.02s (system mean cpu 0%, single max cpu 0%), peaked 0.0 MiB above final usage, current RAM usage now 55.1 MiB

In [3]: import numpy as np
In [3] used 14.6 MiB RAM in 0.25s (system mean cpu 15%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 69.8 MiB

In [4]: np.ones(int(1e10));
In [4] used -27.9 MiB RAM in 35.58s (system mean cpu 10%, single max cpu 100%), peaked 57458.3 MiB above final usage, current RAM usage now 54.1 MiB


```

Francesc Alted has a fork with more memory delta details, see it here: https://github.com/FrancescAlted/ipython_memwatcher

For a demo using numpy and Pandas take a look at [examples/example_usage_np_pd.ipynb](https://github.com/ianozsvald/ipython_memory_usage/blob/master/src/ipython_memory_usage/examples/example_usage_np_pd.ipynb). __Note that this is not up to date__

Setup
=====

Supported: Python 3.8+ and IPython 7.9+

Simple: 

`$ pip install ipython_memory_usage` 

via https://pypi.org/project/ipython-memory-usage/

OR

Take a copy of the code or fork from https://github.com/ianozsvald/ipython_memory_usage and then:

    $ python setup.py install

If you pull it from github and you want to develop on it, it is easier to make a link in `site-packages` and develop it locally with:

    $ pip install -e .

To uninstall:

    $ pip uninstall ipython_memory_usage

Example usage
=============

We can measure on every line how large array operations allocate and deallocate memory:

For the beginner with numpy it can be easy to work on copies of matrices which use a large amount of RAM. The following example sets the scene and then shows an in-place low-RAM variant.

First we make a random square array and modify it twice using copies taking 2.3GB RAM:
```    
In [1]: %load_ext ipython_memory_usage
Enabling IPython Memory Usage, use %imu_start to begin, %imu_stop to end
In [2]: %imu_start

In [3]: a = np.random.random((int(1e4),int(1e4)))
In [3] used 763.3 MiB RAM in 1.82s (system mean cpu 7%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 832.5 MiB

In [4]: b = a*2
In [4] used 762.9 MiB RAM in 0.32s (system mean cpu 6%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 1595.5 MiB

In [5]: c = np.sqrt(b)
In [5] used 762.8 MiB RAM in 0.39s (system mean cpu 7%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 2358.3 MiB
```


Now we do the same operations but in-place on `a`, using 813MB RAM in total:
```
In [3]: a = np.random.random((int(1e4),int(1e4)))
In [3] used 0.1 MiB RAM in 0.92s (system mean cpu 7%, single max cpu 100%), peaked 761.9 MiB above final usage, current RAM usage now 832.5 MiB

In [4]: a *= 2
In [4] used 0.1 MiB RAM in 0.18s (system mean cpu 6%, single max cpu 16%), peaked 0.0 MiB above final usage, current RAM usage now 832.6 MiB

In [5]: a = np.sqrt(a, out=a)
In [5] used 0.0 MiB RAM in 0.25s (system mean cpu 4%, single max cpu 50%), peaked 0.0 MiB above final usage, current RAM usage now 832.6 MiB
```

Lots of `numpy` functions have in-place operations that can assign their result back into themselves (see the `out` argument): http://docs.scipy.org/doc/numpy/reference/ufuncs.html#available-ufuncs


Newer (2020+) versions of Numpy use temporary objects which provide memory optimisation, see https://docs.scipy.org/doc/numpy-1.13.0/release.html

`a` and `b` are multiplied into a temprorary, then the same temporary is re-used for the addition with `c` which is then assigned to `c` so only one circa 700MB array is created. In older versions of numpy several arrays could be created during the same operation.

```
In [3]: a = np.ones(int(1e8)); b = np.ones(int(1e8)); c = np.ones(int(1e8))
In [3] used 2288.8 MiB RAM in 0.61s (system mean cpu 6%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 2358.4 MiB

In [4]: d = a * b + c
In [4] used 763.3 MiB RAM in 0.53s (system mean cpu 5%, single max cpu 100%), peaked 0.0 MiB above final usage, current RAM usage now 3121.7 MiB
```

Important RAM usage note
========================

It is much easier to debug RAM situations with a fresh IPython shell. The longer you use your current shell, the more objects remain inside it and the more RAM the Operating System may have reserved. RAM is returned to the OS slowly, so you can end up with a large process with plenty of spare internal RAM (which will be allocated to your large objects), so this tool (via memory_profiler) reports 0MB RAM usage. If you get confused or don't trust the results, quit IPython and start a fresh shell, then run the fewest commands you need to understand how RAM is added to the process.


Experimental perf stat report to monitor caching
================================================

__Totally out of date for 2023, this needs a refresh__

I've added experimental support for the `perf stat` tool on Linux. To use it make sure that `perf stat` runs at the command line first. Experimental support of the `cache-misses` event is enabled in this variant script (to use this `cd src/ipython_memory_usage` first):
```
Python 3.4.3 |Anaconda 2.3.0 (64-bit)| (default, Jun  4 2015, 15:29:08) 
IPython 3.2.0 -- An enhanced Interactive Python.
In [1]: %run -i ipython_memory_usage_perf.py
In [2]: start_watching_memory()
```

Here's an example that builds on the previous ones. We build a square matrix with C ordering, we also need a 1D vector of the same size:
```
In [3]: ones_c = np.ones((int(1e4),int(1e4)))
In [4]: v = np.ones(int(1e4))
```

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
 * `psutil` for cpu tracking
 * `perf stat` (Linux only, installed outside of Python using e.g. Synaptic, apt-get etc)

Tested on
=========

* IPython 8.17 with Python 3.12 on Linux 64bit (2023-11)


Developer installation notes
============================

Ian's 2023 update

```
conda create -n ipython_memory_usage python=3.12
conda activate ipython_memory_usage
pip install numpy
pip install ipython

pip install -e . # editable installation

ipython
import ipython_memory_usage
%ipython_memory_usage_start

python -m build # builds an installable
```


These notes are for the Man AHL 2019 Hackathon.

```
conda create -n hackathon_ipython_memory_usage python=3.7
conda activate hackathon_ipython_memory_usage
conda install ipython numpy memory_profiler

mkdir hackathon_ipython_memory_usage
cd hackathon_ipython_memory_usage/
git clone git@github.com:ianozsvald/ipython_memory_usage.git

# note "develop" and not the usual "install" here, to make the local folder editable!
python setup.py develop 

# now run ipython and follow the examples from further above in this README
```

```
# make a development environment
$ mkdir ipython_memory_usage_dev
$ cd ipython_memory_usage_dev/
$ conda create -n ipython_memory_usage_dev python=3.9 ipython jupyter memory_profiler numpy pandas
$ conda activate ipython_memory_usage_dev
git clone git@github.com:ianozsvald/ipython_memory_usage.git

# note "develop" and not the usual "install" here, to make the local folder editable!
$ python setup.py develop 

# now run ipython and follow the examples from further above in this README
```

 Acknowledgements
 ================
 
 Many thanks to https://github.com/manahl/ for hosting their 2019-11 hackathon. Here we removed old Python 2.x code, added an IPython magic, validated that Python 3.8 is supported and (very nearly) have a working conda recipe. Thanks to my colleagues:
 * https://github.com/ps-git
 * https://github.com/erdincmutlu
 * https://github.com/Stefannn
 * https://github.com/valmal
 * https://github.com/PauleGef
 * Elices 

 Many thanks to https://github.com/manahl/ for hosting a hackathon (2018-04) that led to us publishing `ipython_memory_usage` to PyPi: https://pypi.org/project/ipython-memory-usage/ . Props to my colleagues for helping me fix the docs and upload to PyPI:
* https://github.com/pawellee
* https://github.com/takumab
* https://github.com/Hexal7785 (Hetal)
* https://github.com/robmarkcole
* https://github.com/pmalde
* https://github.com/LucijaGregov
* https://github.com/xhochy

TO FIX
======

 * merge perf variation into the main variation as some sort of plugin (so it doesn't interfere if per not installed or available)
 * possibly try to add a counter for the size of the garbage collector, to see how many temp objects are made (disable gc first) on each command?
 * conda installation is really out of date `$ conda install -c conda-forge ipython_memory_usage` via https://anaconda.org/conda-forge/ipython_memory_usage
* Should I keep __version__ in ipython_memory_usage.py in addition to pyproject.toml?
  * https://stackoverflow.com/questions/72167802/adding-version-attribute-to-python-module
* Should twine be in the build dependencies in .toml?
* How to add developer dependencies like black?
* For conda how do I specify the source package when it isn't uploaded yet?


Problems
========

 * I can't figure out how to hook into live In prompt (at least - I can for static output, not for a dynamic output - see the code and the commented out blocks referring to `watch_memory_prompt`)
 
Notes to Ian
============

To push to PyPI I need to follow https://packaging.python.org/en/latest/tutorials/packaging-projects/:
* pip install -U twine
* update version in pyproject.toml
* python -m build
* check the dist/ folder only has the current build, 1 whl and 1 zip
* python -m twine upload --repository testpypi dist/*
  * username is __token__, password is the token in my passwords
* python -m twine upload --repository pypi dist/* # when ready
  
