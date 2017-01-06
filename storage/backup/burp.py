#!/usr/bin/python2.7

import json
import sys
import os
from lib.burpserver import BurpServer
from lib import log
from lib import config
# import pprint

# IMPORTANT. FIELDS STILL NEED RENAMING!

if len(sys.argv) != 2:
    print 'ERROR: got invalid arguments. Got this: %s' % sys.argv
    print 'Usage: python backup-burp-linux.py <name of the backuped server>'
    sys.exit(1)

check_folder = sys.argv[1]

log.logger.info('Gathering data of %s' % check_folder)
burpserver = BurpServer(check_folder, root_folder='/tmp')
stats = burpserver.get_backup_stats()
# pprint.pprint(stats)
json_location = config.get('output_file', 'backup-burp-linux')

with open(json_location, 'a') as jsonfile:
    log.logger.debug('Writing stats of %s' % check_folder)
    json.dump(stats, jsonfile)
    jsonfile.write('\n')
    log.logger.debug('Done writing file %s' % json_location)
