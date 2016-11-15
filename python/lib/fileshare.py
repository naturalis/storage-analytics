import os, scandir, subprocess
from os.path import join, getsize, isfile, isdir, splitext
from . import log

def GetFolderSize(path):
    TotalSize = 0
    TotalCount = 0
    for item in scandir.walk(path):
        for file in item[2]:
            try:
                Size = getsize(join(item[0], file))
                TotalSize = TotalSize + Size
                TotalCount = TotalCount + 1
                #TopTen = FindTopTen(TopTen,Size)
            except:
                print("error with file:  " + join(item[0], file))
    return { 'size':TotalSize,'count':TotalCount}


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

def GetFolderOwner(folder,share_type):
    owner_shell = subprocess.Popen(['getfacl',folder],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = owner_shell.communicate()
    owner = []
    if share_type == 'homedir':
        for i in out.split('\n'):
            # owner: NNM\134hans.kruijer
            if i.startswith('# owner:'):
                owner.append(i[13:])
        return owner[0]
    elif share_type == 'groups':
        for i in out.split('\n'):
            if i.startswith('default:group:map'):
                owner.append(i[26:-4])
        if len(owner) == 0:
            return 'Map resource not found'
        else:
            return  'Map - %s' % owner[0]
    else:
        return '_unknown'
