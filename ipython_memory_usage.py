import memory_profiler
import time
import threading
import datetime
import sys

# %run -i memory_watcher.py
# it'll run as a separate thread, writing to the log file

#WATCHER_FILENAME = "memory_usage.log"

# problems:
# long running operations (e.g. np.ones(1e8)) which take a fraction of a second
# to complete might be reported on whilst memory is still growing...

def watch_memory():
    #with open(WATCHER_FILENAME, 'w') as f:
    #    f.write("Memory logger (very hacked together!) - \ntime, mem delta, mem usage, cmd\n")
    print "Memory logger (very hacked together!) - \ntime, mem delta, mem usage, cmd\n"
    nbr_commands = len(In)
    memory_usage = memory_profiler.memory_usage()[0]
    while True:
        #if len(In) != nbr_commands:
        new_memory_usage = memory_profiler.memory_usage()[0]
        memory_delta = new_memory_usage - memory_usage
        #print memory_delta, type(memory_delta), len(In), In
        #if memory_delta > 0 or len(In) != nbr_commands:
        #if len(In) != nbr_commands:  # works
        if len(In) != nbr_commands or memory_delta > 0:
            new_cmd = False
            if nbr_commands != len(In):
                new_cmd = True
                nbr_commands = len(In)
            output = datetime.datetime.now(), memory_delta, new_memory_usage, In[nbr_commands-1]  # , In[nbr_commands]
            #with open(WATCHER_FILENAME, 'a') as f:
            #    if new_cmd:
            #        f.write("\n")
            #    f.write(str(output) + "\n")
            if new_cmd:
                print
            print str(output)
            sys.stdout.flush()
            memory_usage = new_memory_usage
        time.sleep(0.1)

if __name__ == "__main__":
    print "Memory watcher started"  # , writing log to:", WATCHER_FILENAME
    memory_watcher_thread = threading.Thread(target=watch_memory, args = ())
    memory_watcher_thread.daemon = True
    memory_watcher_thread.start()

