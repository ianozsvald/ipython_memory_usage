import memory_profiler
import threading

# %run -i memory_watcher.py

previous_call_memory_usage = memory_profiler.memory_usage()[0]

def watch_memory2():
    import time
    global previous_call_memory_usage
    memory_usage = previous_call_memory_usage
    last_memory_usage = previous_call_memory_usage
    t1 = time.time()
    nbr_commands = len(In)
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
    previous_call_memory_usage = new_memory_usage


if __name__ == "__main__":
    ip = get_ipython()
    ip.events.register("post_run_cell", watch_memory2)

####### OLD EXPERIMENTAL CODE  ###########
def watch_memory(*args, **kwargs):
    #import pdb; pdb.set_trace()
    """After every new command (update to In[]), report new RAM usage caused by last command"""
    import time
    #if 'In' not in dir():
    #    raise ValueError("You must run this from within IPython")
    #    In = None  # dummy to avoid pyflakes
    nbr_commands = len(In)
    while True:
        memory_usage = memory_profiler.memory_usage()[0]
        if len(In) != nbr_commands:  #  or memory_delta > 0:
            t1 = time.time()
            #if nbr_commands != len(In):
                #nbr_commands = len(In)
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
            memory_usage = new_memory_usage
        time.sleep(0.05)


if __name__ == "__main__X":
    print "IPython Memory usage reporter has started (exit IPython to stop using it)"
    if 'In' not in dir():
        raise ValueError("You must run this from IPython interactively using e.g. '%run -i <thisscript>'")
    ipython_memory_usage_thread = threading.Thread(target=watch_memory)
    ipython_memory_usage_thread.daemon = True
    ipython_memory_usage_thread.start()

