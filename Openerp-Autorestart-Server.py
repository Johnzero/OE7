# -*- coding: utf-8 -*-
import os
import win32file
import win32con
import win32api,win32pdhutil
import win32pdh,string
import psutil
import thread

FILE_LIST_DIRECTORY = 0x0001

path_to_watch = "E:\OE7"
OPENERP_BAT_PATH = "E:\\OE7\\v7.bat" # python openerp-server -c install/openerp-server.conf
DICT_TO_WATCH = ["py","xml","conf"]

ACTIONS = {
    1 : "Created",
    2 : "Deleted",
    3 : "Updated",
    4 : "Renamed from something",
    5 : "Renamed to something"
}

#ID = win32api.ShellExecute(0, 'open', OPENERP_BAT_PATH, '','',1)
#os.system(OPENERP_BAT_PATH)

hDir = win32file.CreateFile (
    path_to_watch,
    FILE_LIST_DIRECTORY,
    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    None,
    win32con.OPEN_EXISTING,
    win32con.FILE_FLAG_BACKUP_SEMANTICS,
    None
)

def file_detected():
    while 1:

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
            endwith = file.split(".")
            t = False
            print file, ACTIONS.get (action, "Unknown")
            if endwith[-1] in DICT_TO_WATCH:
                for p in psutil.process_iter():
                    try: 
                        if path_to_watch in p.getcwd():
                            if p.parent.name == "cmd.exe":
                                p.kill()
                                print '-------------------------------------------------------------'
                                print '----------------------Server Restart-------------------------','\n'
                                thread.start_new_thread(openerp_server,())
                    except psutil.AccessDenied:pass

def  openerp_server():
    os.system(OPENERP_BAT_PATH)

if __name__ == '__main__':
    thread.start_new_thread(openerp_server,())
    file_detected()
