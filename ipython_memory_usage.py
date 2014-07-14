import memory_profiler
import threading


# %run -i memory_watcher.py
# it'll run as a separate thread, writing to the log file

#WATCHER_FILENAME = "memory_usage.log"

# problems:
# long running operations (e.g. np.ones(1e8)) which take a fraction of a second
# to complete might be reported on whilst memory is still growing...


def watch_memory():
    """After every new command (update to In[]), report new RAM usage caused by last command"""
    import time
    nbr_commands = len(In)
    memory_usage = memory_profiler.memory_usage()[0]
    while True:
        if len(In) != nbr_commands:  #  or memory_delta > 0:
            t1 = time.time()
            new_cmd = False
            if nbr_commands != len(In):
                new_cmd = True
                nbr_commands = len(In)
            last_memory_usage = memory_usage
            while True:
                new_memory_usage = memory_profiler.memory_usage()[0]
                memory_delta = new_memory_usage - last_memory_usage
                if memory_delta > 0:
                    # wait whilst RAM allocations settle down
                    time.sleep(0.01)
                    last_memory_usage = new_memory_usage
                else:
                    break
            memory_delta = new_memory_usage - memory_usage
            time_delta_secs = time.time() - t1
            output = "'{cmd}' used {memory_delta:0.4f} MiB RAM in {time_delta:0.2f}s, total RAM usage {memory_usage:0.2f} MiB".format(time_delta=time_delta_secs, cmd=In[nbr_commands-1], memory_delta=memory_delta, memory_usage=new_memory_usage)
            print str(output)
            #sys.stdout.flush()
            memory_usage = new_memory_usage
        time.sleep(0.05)

if __name__ == "__main__":
    print "IPython Memory usage reporter has started (exit IPython to stop using it)"
    if 'In' not in dir():
        raise ValueError("You must run this from IPython interactively using e.g. '%run -i <thisscript>'")
    ipython_memory_usage_thread = threading.Thread(target=watch_memory)
    ipython_memory_usage_thread.daemon = True
    ipython_memory_usage_thread.start()

