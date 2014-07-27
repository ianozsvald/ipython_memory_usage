import subprocess
import unittest

FIXTURE0 = """     0.100167119              3,183 cache-misses   """
ANSWER0 = 3183
FIXTURE1 = """#           time             counts events\n     0.100167119              3,183 cache-misses             \n     0.200354348              4,045 cache-misses             \n     """
ANSWER1 = [3183, 4045]
FIXTURE2 = """     3.501390851        471,219,787 stalled-cycles-frontend\n  14.005319456          2,249,115 stalled-cycles-frontend  """
ANSWER2 = [471219787,  2249115]


def process_line(line):
    """Process a single output line from perf-stat, extract only a value (skip help lines)"""
    line_bits = line.split()
    try:
        value = float(line_bits[1].replace(',', ''))
    except ValueError:
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


proc = None
keep_running = None

def run_capture_perf(pid=None):
    if not pid:
        import os
        pid = os.getpid()
        print "Using PID", pid
    global proc, keep_running
    import time
    cmd = "perf stat --pid {pid} --event cache-misses -I 100".format(pid=pid)
    proc = subprocess.Popen(cmd.split(), stderr=subprocess.PIPE)
    while keep_running:
        time.sleep(0.1)

def finish_perf():
    # once the job has finished, kill recording
    global proc
    proc.kill()
    (stdoutdata, stderrdata) = proc.communicate()
    # example stderrdata output:
    # #           time             counts events
    # 0.100173796              2,761 cache-misses
    # 0.200387519              4,232 cache-misses
    # 0.300540762              5,277 cache-misses
    # 0.400778748              3,916 cache-misses
    values = process_lines(stderrdata)
    return values


def start_thread(pid):
    import threading
    ipython_memory_usage_thread = threading.Thread(target=run_capture_perf, args=(pid,))
    ipython_memory_usage_thread.daemon = True
    ipython_memory_usage_thread.start()

if __name__ == "__main__":
    pid = 2997
    start_thread(pid)
    import time
    time.sleep(0.5)
    keep_running = False
    values = finish_perf()
    print values

if __name__ == "__main__X":
    pid = 2997
    #import os
    #os.getpid(pid)
    run_capture_perf()  # pid)
    import time
    time.sleep(0.5)
    keep_running = False
    values = finish_perf()
    print values
