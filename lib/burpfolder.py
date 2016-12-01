import os, scandir, subprocess
from os.path import join, getsize, isfile, isdir, splitext
import socket, datetime, pprint
from . import log

def buro_folder_info(folder,c):
    """
    Gathers information and statistics of a AD sharded folder
    * Path of dir
    * AD connection object
    Returns a dict with statistics
    """
    total = _get_folder_size(folder)
    json_dict = {'data_size':total['size'],
                 'timestamp': datetime.datetime.now().isoformat(),
                 'data_amount':total['count'],
                 'host': socket.getfqdn(),
#                 'data_set':dataset,
#                 'data_groups': group_access,
#                 'data_owner': data_owner,
                 'storage_type': 'fileshare',
                 'storage_pool': 'volumes',
                 'storage_location': 'primary-cluster-001',
                 'data_status': 'production',
                 'data_host': socket.getfqdn(),
                 'storage_path' : 'smb://%s/%s/%s' % (socket.getfqdn(),share_type,folder.split('/')[-1]),
                 'data_service_tags' : [socket.gethostname().split('-')[0],socket.gethostname().split('-')[1]]
                 }
    return json_dict

def _get_folder_size(path):
    """
    Private: get folder size
    * Path of dir
    Returns dict with total size (bytes) and total number of files.
    """
    TotalSize = 0
    TotalCount = 0
    for item in scandir.walk(path):
        for file in item[2]:
            try:
                Size = getsize(join(item[0], file))
                TotalSize = TotalSize + Size
                TotalCount = TotalCount + 1
            except:
                print("error with file:  " + join(item[0], file))
    return { 'size':TotalSize,'count':TotalCount}


