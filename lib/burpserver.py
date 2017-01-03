import os, scandir, subprocess
#from os.path import join, getsize, isfile, isdir, splitext
import socket, datetime
from . import log



class BurpServer:
    def __init__(self,target_server,root_folder='/mnt/backup/burpdata'):
        """
        Initialises burp class.
        * target_server -> server which is backupped
        * root_folder ->  folder where backups are stored (Default /mnt/backup/burpdata)
        Returns BurpServer class
        """
        self.target_server = target_server
        self.root_folder = root_folder
        self.target = os.path.join(root_folder,target_server)
        print self.target_server
        print self.target
        log.logger.debug('%s Initialized' % self)


    def get_backup_stats(self,separate=False):
        """
        Get sizes of backup of the initiated target server
        Return dict with total sizes and separate sizes of backups
        """
        separate_sizes = []
        total_size = 0
        total_count = 0
        service_tags = socket.gethostname().split('.')[0].split('-')[:2]
        service_tags.append(self.target_server)
        for f in self.__get_backup_folders():
            stat = self.__get_folder_size(os.path.join(self.target,f))
            stat['backupname'] = f
            stat['backupserver'] = self.target_server
            stat['extra_info'] = self.__get_backup_info(os.path.join(self.target,f))
            if separate:
                separate_sizes.append(stat)
            total_size = total_size + stat['size']
            total_count = total_count + stat['count']

        json_dict = {'data_size':total_size,
                 'timestamp': datetime.datetime.now().isoformat(),
                 'data_amount': total_count,
                 'host': socket.getfqdn(),
                 'data_set': '',
                 'data_groups': '',
                 'data_owner': '',
                 'storage_type': 'backup',
                 'storage_pool': 'volumes',
                 'storage_location': 'backup-cluster-001',
                 'data_status': 'production',
                 'data_host': socket.getfqdn(),
                 'storage_path' : self.target,
                 'data_service_tags' : service_tags
                 }
        if separate:
            json_dict['data_service_tags'] = separate_sizes
        return json_dict


    def __get_number_of_backups(self):
        return len(self.__get_backup_folders)

    def __get_backup_folders(self,exclude_folders=['current','working','finishing','lockfile']):
        """
        Private
        Get backup folders
        Returns all folders of target_server
        """
        dirs = []
        for d in os.listdir(self.target):
            if d not in exclude_folders:
                dirs.append(d)
        return dirs

    def __get_folder_size(self,path):
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
                    Size = os.path.getsize(os.path.join(item[0], file))
                    TotalSize = TotalSize + Size
                    TotalCount = TotalCount + 1
                    #TopTen = FindTopTen(TopTen,Size)
                except:
                    log.logger.debug('Error with file: %s  ' % os.path.join(item[0], file))
        return { 'size':TotalSize,'count':TotalCount}

    def __get_backup_info(self,folder,attributes=['bytes_received','bytes_in_backup','bytes_estimated','total_total','total_changed','total_deleted']):
        """
        Private
        * Foldername of the backup
        Returns extra information of the backup
        """
        extra_info = {}
        try:
            with open(os.path.join(folder,'backup_stats')) as f:
                content = f.readlines()
                for c in content:
                    if any(c.startswith(x) for x in attributes):
                        key, val = c.split(':')
                        extra_info[key] = int(val.rstrip())
        except Exception as e:
            log.logger.debug('Unable to open backup_stats')
            log.logger.debug(e)
        return extra_info

# def share_info(folder,c):
#     """
#     Gathers information and statistics of a AD sharded folder
#     * Path of dir
#     * AD connection object
#     Returns a dict with statistics
#     """
#     total = _get_folder_size(folder)
#     share_type = _get_share_type(folder)
#     folder_owner = _get_folder_owner(folder,share_type)
#
#     group_access = {}
#     if share_type == 'groups' and folder_owner is not 'Map resource not found':
#         group_access = ad.groups_in_group(c,folder_owner)
#     data_owner = {}
#     if share_type == 'homedir' and folder_owner is not 'User not found':
#         do = ad.user_info(c,folder_owner,['userPrincipalName','objectGUID'])
#         if isinstance(do,dict):
#             data_owner = {'name':do['userPrincipalName'],'id':do['objectGUID']}
#
#     ds = ad.group_info(c,folder_owner,['name','objectGUID'])
#     dataset = {}
#     if isinstance(ds,dict):
#         dataset = {'name':ds['name'],'id':ds['objectGUID']}
#
#     json_dict = {'data_size':total['size'],
#                  'timestamp': datetime.datetime.now().isoformat(),
#                  'data_amount':total['count'],
#                  'host': socket.getfqdn(),
#                  'data_set':dataset,
#                  'data_groups':group_access,
#                  'data_owner': data_owner,
#                  'storage_type': 'fileshare',
#                  'storage_pool': 'volumes',
#                  'storage_location': 'primary-cluster-001',
#                  'data_status': 'production',
#                  'data_host': socket.getfqdn(),
#                  'storage_path' : 'smb://%s/%s/%s' % (socket.getfqdn(),share_type,folder.split('/')[-1]),
#                  'data_service_tags' : [socket.gethostname().split('-')[0],socket.gethostname().split('-')[1]]
#                  }
#     return json_dict
#
# def _get_folder_size(path):
#     """
#     Private: get folder size
#     * Path of dir
#     Returns dict with total size (bytes) and total number of files.
#     """
#     TotalSize = 0
#     TotalCount = 0
#     for item in scandir.walk(path):
#         for file in item[2]:
#             try:
#                 Size = getsize(join(item[0], file))
#                 TotalSize = TotalSize + Size
#                 TotalCount = TotalCount + 1
#                 #TopTen = FindTopTen(TopTen,Size)
#             except:
#                 print("error with file:  " + join(item[0], file))
#     return { 'size':TotalSize,'count':TotalCount}
#
#
# def _find_top_ten(current,candidate,size=10):
#     """
#     Private: find top ten highest numbers
#     * current list
#     * new candidate
#     * (optional) size of list. default=10
#     Returns array with top
#     """
#     if len(current) == 0:
#         current.append(candidate)
#     else:
#         if candidate > current[0]:
#             current.append(candidate)
#         current = sorted(current)
#         if len(current) > size:
#             del current[0]
#
#     return current
#
# def _get_share_type(folder):
#     """
#     Private: get share type (homedir or group share)
#     * Path of dir
#     Returns string with type
#     """
#     share_type = subprocess.Popen(['net','rpc','share','list','-U','anomynous','-P','nopass'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#     out, err = share_type.communicate()
#     share_tp = []
#     for i in out.split('\n'):
#         if i[-1:] is not '$' or not i.strip():
#             share_tp.append(i)
#     return share_tp[0]
#
# def _get_folder_owner(folder,share_type):
#     """
#     Private: get owner of folder
#     * Path of dir
#     * share_type (homedir / groups)
#     Returns string with owner
#     """
#     owner_shell = subprocess.Popen(['getfacl',folder],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#     out, err = owner_shell.communicate()
#     owner = []
#     if share_type == 'homedir':
#         for i in out.split('\n'):
#             # owner: NNM\134hans.kruijer
#             if i.startswith('# owner:'):
#                 owner.append(str(i[13:]))
#         return owner[0]
#     elif share_type == 'groups':
#         for i in out.split('\n'):
#             if i.startswith('default:group:map'):
#                 owner.append(i[26:-4])
#         if len(owner) == 0:
#             return 'Map resource not found'
#         else:
#             return  'Map - %s' % owner[0]
#     else:
#         return '_unknown'
