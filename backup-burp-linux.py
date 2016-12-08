#!/usr/bin/python2.7

import json, sys, os
from lib.burpserver import BurpServer
from lib import log
import pprint
#checkfolder = sys.argv[1]



#_SHARE = '/data'
#_JSON_LOCATION = '/tmp/stats.json'

# user = config.get('ad_user')
# password = config.get('ad_password')
# domain = config.get('ad_domain') + '\\'
# to_address = config.get('account_mail_to')
# host = config.get('ad_host')
#share = config.get('share_folder','fileshare')
#json_location = config.get('output_file','fileshare')
__BURP_MOUNT__ = '/mnt/backup/burpdata'

log.logger.info('Starting gathering data this backupserver')
for d in os.listdir(__BURP_MOUNT__):
    path = os.path.join(__BURP_MOUNT__,d)
    if os.path.isdir(path):
        log.logger.info('Gathering data of %s' % path)
        burpserver = BurpServer(d)
        stats = burpserver.get_backup_stats()
        pprint.pprint(stats)
# if c.bind():
#     log.logger.info('Checking usage of share %s' % share)
#     for d in os.listdir(share):
#         if os.path.isdir(os.path.join(share,d)):
#             with open(json_location,'a') as jsonfile:
#                 log.logger.debug('Checking folder %s' % d)
#                 json.dump((fs.share_info(os.path.join(share,d),c)),jsonfile)
#                 jsonfile.write('\n')
#                 log.logger.debug('Done with folder %s' % d)
# c.unbind()
