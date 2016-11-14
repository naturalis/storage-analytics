#!/usr/bin/python2.7

from os import environ
from lib import ad as ad
#from lib import ks as ks
from lib import log as log
from lib import config as config
from lib import fileshare as fs

_SHARE = '/data/Servoy Images'
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
    print "Usage: %s GB" % str(round(float(total) /1024 /1024 /1024,2))
    print "Share type: %s" % fs.GetShareType(folder)
    print "Share Onwer: %s " % fs.GetFolderOwner(folder)
    print "Groups with access: %s" % ad.groups_in_group(c,fs.GetFolderOwner(folder))



#ksclient = ks.connect(auth_url,ks_username,ks_password,project_name)

if c.bind():
    log.logger.info('Checking usage of share %s' % _SHARE)
    share_info(_SHARE)
c.unbind()
