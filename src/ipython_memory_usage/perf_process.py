""""""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import subprocess
import unittest
import os

FIXTURE0 = """     0.100167119              3,183 cache-misses   """
ANSWER0 = 3183
FIXTURE1 = """#           time             counts events\n     0.100167119              3,183 cache-misses             \n     0.200354348              4,045 cache-misses             \n     """
ANSWER1 = [3183, 4045]
FIXTURE2 = """     3.501390851        471,219,787 stalled-cycles-frontend\n  14.005319456          2,249,115 stalled-cycles-frontend  """
ANSWER2 = [471219787,  2249115]


EVENT_TYPE_CM = "cache-misses"
EVENT_TYPE_SCF = "stalled-cycles-frontend"
EVENT_TYPE_I = "instructions"
EVENT_TYPES = set([EVENT_TYPE_CM, EVENT_TYPE_SCF, EVENT_TYPE_I])
EVENT_TYPE = EVENT_TYPE_CM

def process_line(line):
    """Process a single output line from perf-stat, extract only a value (skip help lines)"""
    line_bits = line.split()
    #print(line_bits)
    try:
        value = float(line_bits[1].replace(',', ''))
    except ValueError:
        if line_bits[2] in EVENT_TYPES:
            # we only get here if we've got a value and a key
            key = line_bits[2]
        value = None
    except IndexError:
        value = None
    return value


def process_lines(lines):
    """Process many lines of perf-stat output, extract the values"""
    # we're assuming we have \n as line endings in this long string
    values = []
    for line in lines.split('\n'):
        value = process_line(line)
        if value:
            values.append(value)
    return values


class Test(unittest.TestCase):
    def test1(self):
        answer0 = process_line(FIXTURE0)
        self.assertEqual(ANSWER0, answer0)

    def test_process_lines(self):
        values = process_lines(FIXTURE0)
        self.assertEqual(values, [ANSWER0])

    def test_process_lines2(self):
        # check we can process the cache-misses messages
        values = process_lines(FIXTURE1)
        self.assertEqual(values, ANSWER1)

        # check that if we have repeated help messages, we still extract the
        # values we expect
        values = process_lines(FIXTURE1+FIXTURE1)
        self.assertEqual(values, ANSWER1+ANSWER1)

    def test_process_lines3(self):
        # check we can process stalled-cycles-frontend messages
        values = process_lines(FIXTURE2)
        self.assertEqual(values, ANSWER2)


def run_capture_perf(pid):
    """Start a perf stat process monitoring pid every 100ms"""
    cmd = "perf stat --pid {pid} --event {event_type} -I 100".format(pid=pid, event_type=EVENT_TYPE)
    #print("run_capture_perf running:", cmd)  # debug message
    proc = subprocess.Popen(cmd.split(), stderr=subprocess.PIPE)
    return proc


def finish_perf(proc):
    """Finish collecting data, parse and return"""
    # once the job has finished, kill recording
    proc.kill()
    # now block to gather all output data
    (stdoutdata, stderrdata) = proc.communicate()
    # example stderrdata output:
    # #           time             counts events
    # 0.100173796              2,761 cache-misses
    # 0.200387519              4,232 cache-misses
    # 0.300540762              5,277 cache-misses
    # 0.400778748              3,916 cache-misses
    stderrdata = stderrdata.decode('ascii')  # assume ascii
    values = process_lines(stderrdata)
    return values


if __name__ == "__main__":
    # simple test for a hardcoded pid gathered over 0.5 seconds
    pid = os.getpid()
    print("Using pid:", pid)
    proc = run_capture_perf(pid)
    import time
    time.sleep(0.5)
    values = finish_perf(proc)
    print(values)
