import memory_profiler
import threading

# %run -i memory_watcher.py

# keep a global accounting for the last known memory usage
# which is the reference point for the memory delta calculation
previous_call_memory_usage = memory_profiler.memory_usage()[0]

from IPython.core.prompts import LazyEvaluate
#  variant that runs inside the IPy In prompt, but is broken in that it
# only updates once and then not again
# http://ipython.org/ipython-doc/dev/api/generated/IPython.core.prompts.html
#@LazyEvaluate
def watch_memory_prompt():
    import time
    # bring in the global memory usage value from the previous iteration
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
    # note that long strings raise an error in IPython, hence this short output
    output = u"{memory_delta:0.4f} MiB RAM".format(time_delta=time_delta_secs, cmd=In[nbr_commands-1], memory_delta=memory_delta, memory_usage=new_memory_usage)
    previous_call_memory_usage = new_memory_usage
    return output


def watch_memory():
    import time
    # bring in the global memory usage value from the previous iteration
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
    # http://ipython.org/ipython-doc/dev/api/generated/IPython.core.events.html
    ip.events.register("post_run_cell", watch_memory)  # WORKS WELL

    #ip.set_hook("pre_prompt_hook", dummy)  # gives lots of stuff to dummy, does not set prompt
    # def dummy(arg) ... where arg is an interactiveshell

    # %config PromptManager.in_template="${watch_memory_prompt()}"
    # this will work but doesn't want to update interactively

####### OLD EXPERIMENTAL CODE  ###########
#def watch_memory(*args, **kwargs):
    ##import pdb; pdb.set_trace()
    #"""After every new command (update to In[]), report new RAM usage caused by last command"""
    #import time
    ##if 'In' not in dir():
    ##    raise ValueError("You must run this from within IPython")
    ##    In = None  # dummy to avoid pyflakes
    #nbr_commands = len(In)
    #while True:
        #memory_usage = memory_profiler.memory_usage()[0]
        #if len(In) != nbr_commands:  #  or memory_delta > 0:
            #t1 = time.time()
            ##if nbr_commands != len(In):
                ##nbr_commands = len(In)
            #nbr_commands = len(In)
            #last_memory_usage = memory_usage
            #while True:
                #new_memory_usage = memory_profiler.memory_usage()[0]
                #memory_delta = new_memory_usage - last_memory_usage
                #if memory_delta > 0:
                    ## wait whilst RAM allocations settle down
                    #time.sleep(0.01)
                    #last_memory_usage = new_memory_usage
                #else:
                    #break
            #memory_delta = new_memory_usage - memory_usage
            #time_delta_secs = time.time() - t1
            #output = "'{cmd}' used {memory_delta:0.4f} MiB RAM in {time_delta:0.2f}s, total RAM usage {memory_usage:0.2f} MiB".format(time_delta=time_delta_secs, cmd=In[nbr_commands-1], memory_delta=memory_delta, memory_usage=new_memory_usage)
            #print str(output)
            #memory_usage = new_memory_usage
        #time.sleep(0.05)


#if __name__ == "__main__X":
    #print "IPython Memory usage reporter has started (exit IPython to stop using it)"
    #if 'In' not in dir():
        #raise ValueError("You must run this from IPython interactively using e.g. '%run -i <thisscript>'")
    #ipython_memory_usage_thread = threading.Thread(target=watch_memory)
    #ipython_memory_usage_thread.daemon = True
    #ipython_memory_usage_thread.start()

