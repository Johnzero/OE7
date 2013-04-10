# -*- coding: utf-8 -*-
import os
import win32file
import win32con
import win32api,win32pdhutil
import win32pdh,string
import psutil

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Updated",
    4 : "Renamed from something",
    5 : "Renamed to something"
}
# Thanks to Claudio Grondi for the correct set of numbers
FILE_LIST_DIRECTORY = 0x0001
path_to_watch = "J:\openerp-7.0"
OPENERP_BAT_PATH = "J:\\v7.bat"
DICT_TO_WATCH = ["py","xml"]

ID = win32api.ShellExecute(0, 'open', OPENERP_BAT_PATH, '','',1)

hDir = win32file.CreateFile (
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)

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
        #full_filename = os.path.join (path_to_watch, file)
        print file, ACTIONS.get (action, "Unknown")
        endwith = file.split(".")
        t = False
        if endwith[-1] in DICT_TO_WATCH:
            for p in psutil.process_iter():
                if p.get_connections():
                    if 8069 in p.get_connections()[0].local_address:
                        p.kill()
                        t = True
                        #win32api.ShellExecute(0, 'open', OPENERP_BAT_PATH, '','',1)
            if t:win32api.ShellExecute(0, 'open', OPENERP_BAT_PATH, '','',1)
            print '\n'