#!/usr/bin/python2.7

import pprint

import json, socket, datetime
from os import environ
from lib import ad as ad
#from lib import ks as ks
from lib import log as log
from lib import config as config
from lib import fileshare as fs


_SHARE = '/data/Eis'
#auth_url = 'http://' + config.get(own'admin_endpoint_ip') + ':35357/v3'
#ks_username = config.get('os_username')
#ks_password = config.get('os_password')
#project_name = config.get('os_project_name')
user = config.get('ad_user')
password = config.get('ad_password')
domain = config.get('ad_domain') + '\\'
to_address = config.get('account_mail_to')
host = config.get('ad_host')
#ks_ad_group_sync_id = config.get('ks_ad_group_sync_id')

c = ad.connect(host,domain+user,password)

def share_info(folder):
    total = fs.GetFolderSize(folder)
    share_type = fs.GetShareType(folder)
    folder_owner = fs.GetFolderOwner(folder,share_type)

    group_access = {}
    if share_type == 'groups' and folder_owner is not 'Map resource not found':
        group_access = ad.groups_in_group(c,folder_owner)
    data_owner = {}
    if share_type == 'homedir' and isinstance(folder_owner,dict):
        do = ad.user_info(c,folder_owner,['name','objectGUID'])
        if isinstance(do,dict):
            data_owner = {'name':do['name'],'id':do['objectGUID']}

    ds = ad.group_info(c,folder_owner,['name','objectGUID'])
    dataset = {}
    if isinstance(ds,dict):
        dataset = {'name':ds['name'],'id':ds['objectGUID']}

    json_dict = {'data_size':total['size'],
                 'timestamp': datetime.datetime.now().isoformat(),
                 'data_amount':total['count'],
                 'host': socket.getfqdn(),
                 'data_set':dataset,
                 'data_groups':group_access,
                 'data_owner': data_owner,
                 'storage_type': 'fileshare',
                 'storage_pool': 'volumes',
                 'storage_location': 'primary-cluster-001',
                 'data_status': 'production',
                 'data_host': socket.getfqdn(),
                 'storage_path' : 'smb://%s/%s/%s' % (socket.getfqdn(),share_type,folder.split('/')[-1]),
                 'data_service_tags' : [socket.gethostname().split('-')[0],socket.gethostname().split('-')[1]]
                 }
    pprint.pprint(json_dict)
#ksclient = ks.connect(auth_url,ks_username,ks_password,project_name)

if c.bind():
    log.logger.info('Checking usage of share %s' % _SHARE)
    share_info(_SHARE)
c.unbind()
