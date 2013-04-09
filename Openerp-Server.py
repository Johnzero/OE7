# -*- coding: utf-8 -*-
import os
import win32file
import win32con
import win32api,win32pdhutil
import win32pdh,string
ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Updated",
    4 : "Renamed from something",
    5 : "Renamed to something"
}

# Thanks to Claudio Grondi for the correct set of numbers
FILE_LIST_DIRECTORY = 0x0001
path_to_watch = "C:\Users\Administrator\Desktop\pyinotify-master"
OPENERP_BAT_PATH = "J:\\V7.bat"


hDir = win32file.CreateFile (
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)

def GetAllProcesses():
    object = "Process"
    items, instances = win32pdh.EnumObjectItems(None,None,object, win32pdh.PERF_DETAIL_WIZARD)
    return instances

def GetProcessID( name ):
    object = "Process"
    items, instances = win32pdh.EnumObjectItems(None,None,object, win32pdh.PERF_DETAIL_WIZARD)
    val = None
    if name in instances :
        hq = win32pdh.OpenQuery()
        hcs = []
        item = "ID Process"
        path = win32pdh.MakeCounterPath( (None,object,name, None, 0, item) )
        hcs.append(win32pdh.AddCounter(hq, path))
        win32pdh.CollectQueryData(hq)
        time.sleep(0.01)
        win32pdh.CollectQueryData(hq)
        for hc in hcs:
            type, val = win32pdh.GetFormattedCounterValue(hc, win32pdh.PDH_FMT_LONG)
            win32pdh.RemoveCounter(hc)
            win32pdh.CloseQuery(hq)
            return val
def Kill_Process_pid(pid) :
    handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pid) #get process handle
    win32api.TerminateProcess(handle,0) #kill by handle
    win32api.CloseHandle(handle) #close api
    # ***********************************************************************
 
 
def Kill_Process ( name ) :
    pid = GetProcessID (name)
    print pid
    if pid:
        print "exist"
        Kill_Process_pid(pid)
    else:
        print "not this proccess"
        
while 1:
  #
  # ReadDirectoryChangesW takes a previously-created
  #  handle to a directory, a buffer size for results,
  #  a flag to indicate whether to watch subtrees and
  #  a filter of what changes to notify.
  #
  # NB Tim Juchcinski reports that he needed to up
  #  the buffer size to be sure of picking up all
  #  events when a large number of files were
  #  deleted at once.
  #
    results = win32file.ReadDirectoryChangesW (
      hDir,
      1024,
      True,
      win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
       win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
       win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
       win32con.FILE_NOTIFY_CHANGE_SIZE |
       win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
       win32con.FILE_NOTIFY_CHANGE_SECURITY,
      None,
      None
    )

    for action, file in results:
        full_filename = os.path.join (path_to_watch, file)
        print full_filename, ACTIONS.get (action, "Unknown")
        os.system('taskkill /im cmd.exe')
        os.system(OPENERP_BAT_PATH)      
        