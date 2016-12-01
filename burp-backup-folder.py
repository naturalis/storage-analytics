#!/usr/bin/python2.7

import json
import os
from lib import log as log
from lib import config as config
from lib import burpfolder as folder


#_SHARE = '/data'
#_JSON_LOCATION = '/tmp/stats.json'

share = config.get('share_folder','fileshare')
share = sys.argv[1]
json_location = config.get('output_file','fileshare')

c = ad.connect(host,domain+user,password)

if c.bind():
    log.logger.info('Checking usage of share %s' % share)
    for d in os.listdir(share):
        if os.path.isdir(os.path.join(share,d)):
            with open(json_location,'a') as jsonfile:
                log.logger.debug('Checking folder %s' % d)
                json.dump((folder.burp_folder_info(os.path.join(share,d),c)),jsonfile)
                jsonfile.write('\n')
                log.logger.debug('Done with folder %s' % d)
c.unbind()
