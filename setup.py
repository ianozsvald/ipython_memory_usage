#!/usr/bin/env python
"""ipython_memory_usage: display memory usage during IPython execution

ipython_memory_usage is an IPython tool to report memory usage deltas for every command you type.
"""

doclines = __doc__.split("\n")

# Chosen from http://www.python.org/pypi?:action=list_classifiers
classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: Free To Use But Restricted
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
"""

from setuptools import setup, find_packages
setup(
    name="ipython_memory_usage",
    version="1.1",
    url="https://github.com/ianozsvald/ipython_memory_usage",
    author="Ian Ozsvald",
    author_email="ian@ianozsvald.com",
    maintainer="Ian Ozsvald",
    maintainer_email="ian@ianozsvald.com",
    description=doclines[0],
    long_description = """IPython tool to report memory usage deltas for every command you type. If you are running out of RAM then use this tool to understand what's happening. It also records the time spent running each command. \n

        In [3]: arr=np.random.uniform(size=int(1e7))\n
        'arr=np.random.uniform(size=int(1e7))' used 76.2578 MiB RAM in 0.33s, peaked 0.00 MiB above current, total RAM usage 107.37 MiB
    """,
    long_description_content_type='text/markdown',
    classifiers=filter(None, classifiers.split("\n")),
    platforms=["Any."],
    packages=['ipython_memory_usage'],
    package_dir={'': 'src'},
    install_requires=['IPython>=2.1', 'memory_profiler']
)
