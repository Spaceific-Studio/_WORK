from os import walk
import os
import os.path as osPath
import threading
import time

"""
     test of multithread clasd

"""
#dirPath = r"/storage/emulated/0/Download/rename"
#dirPath = r"/storage/emulated/0/DCIM"
print dir(threading.Thread)
exitFlag = 0

class AsyncTime(threading.Thread):
    """multithread class for time delay process
    """
    def __init__(self, threadID, name, counter): 
        threading.Thread.__init__(self)
        self.threadID = threadID 
        self.name = name 
        self.counter = counter
    
    # Overwritten method of parent class(threading.Thread).
    def run(self):
        print "Starting " + self.name 
        print_time(self.name, 5, self.counter) 
        print "Exiting " + self.name
      
def print_time(threadName, counter, delay):
    """ prints current time of running thread
        
    Args:
        param1 (str): name of thread
        param2 (int): count of loops
        param3 (int): delay between loops
            Default is 0

    Returns:
        nothing

    Raises: not specified yet text under is example template
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `param2` is equal to `param1`.
    """
    while counter:
        if exitFlag:
            threadName.exit() 
        time.sleep(delay)
        print "{0} - {1}".format(threadName, time.ctime(time.time()))
        counter = counter - 1

class SyncTime(threading.Thread):
    """multithread class for time delay process
    """
    def __init__(self, threadID, name, counter): 
        threading.Thread.__init__(self)
        self.threadID = threadID 
        self.name = name 
        self.counter = counter
    
    # Overwritten method of parent class(threading.Thread).
    def run(self):
        print "Starting " + self.name 
        # Get lock to synchronize threads 
        threadLock.acquire() 
        print_sync_time(self.name, self.counter, 3) 
        # Free lock to release next thread 
        threadLock.release()
        
def print_sync_time(threadName, counter, delay):
    """ prints current time of running thread
        
    Args:
        param1 (str): name of thread
        param2 (int): count of loops
        param3 (int): delay between loops
            Default is 0

    Returns:
        nothing

    Raises: not specified yet text under is example template
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `param2` is equal to `param1`.
    """
    while counter:
        time.sleep(delay)
        print "{0} - {1}".format(threadName, time.ctime(time.time()))
        counter = counter - 1      
          
threadLock = threading.Lock() 
threads = [] 


# Create new threads 
thread1 = AsyncTime(1, "Thread-1", 1) 
thread2 = AsyncTime(2, "Thread-2", 2) 
thread3 = SyncTime(3, "Thread-3", 3) 
thread4 = SyncTime(4, "Thread-4", 4) 

# Start new Threads 
thread1.start() 
thread2.start() 
thread3.start() 
thread4.start() 

# Add threads to thread list 
threads.append(thread3) 
threads.append(thread4) 

# Wait for all threads to complete 
for t in threads: 
    t.join() 
for t in threads: 
    print "Exiting {}".format(t.name)
print "Exiting Main Thread"
    
    
        
       