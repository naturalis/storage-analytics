import os, scandir, subprocess
from os.path import join, getsize, isfile, isdir, splitext
from . import log

def GetFolderSize(path):
    TotalSize = 0
    for item in scandir.walk(path):
        for file in item[2]:
            try:
                Size = getsize(join(item[0], file))
                TotalSize = TotalSize + Size
                #TopTen = FindTopTen(TopTen,Size)
            except:
                print("error with file:  " + join(item[0], file))
    return TotalSize


def FindTopTen(current,candidate,size=10):
    if len(current) == 0:
        current.append(candidate)
    else:
        if candidate > current[0]:
            current.append(candidate)
        current = sorted(current)
        if len(current) > size:
            del current[0]

    return current

def GetShareType(folder):
    share_type = subprocess.Popen(['net','rpc','share','list','-U','anomynous','-P','nopass'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = share_type.communicate()
    share_tp = []
    for i in out.split('\n'):
        if i[-1:] is not '$' or not i.strip():
            share_tp.append(i)
    return share_tp[0]

def GetFolderOwner(folder):
    owner_shell = subprocess.Popen(['getfacl',folder],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = owner_shell.communicate()
    owner = []
    for i in out.split('\n'):
        if i.startswith('default:group:map'):
            owner.append(i[26:-4])
    return  'Map - %s' % owner[0]
