#!/usr/bin/python2.7

import json
import os
import sys
from lib import log as log
from lib import config as config
from lib import burpfolder as folder


#_SHARE = '/data'
#_JSON_LOCATION = '/tmp/stats.json'


checkfolder = sys.argv[1]

json_location = config.get('output_file','fileshare')

log.logger.debug('Checking folder %s' % checkfolder)
with open(json_location,'a') as jsonfile:   
  json.dump(folder.burp_folder_info(checkfolder),jsonfile)
  jsonfile.write('\n')
  log.logger.debug('Done with folder %s' % checkfolder)

