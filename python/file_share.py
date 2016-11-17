#!/usr/bin/python2.7

import json
import os

from lib import ad as ad
from lib import log as log
from lib import config as config
from lib import fileshare as fs


_SHARE = '/data'
_JSON_LOCATION = '/tmp/stats.json'

user = config.get('ad_user')
password = config.get('ad_password')
domain = config.get('ad_domain') + '\\'
to_address = config.get('account_mail_to')
host = config.get('ad_host')

c = ad.connect(host,domain+user,password)

if c.bind():
    log.logger.info('Checking usage of share %s' % _SHARE)
    for d in os.listdir(_SHARE):
        if os.path.isdir(os.path.join(_SHARE,d)):
            with open(_JSON_LOCATION,'a') as jsonfile:
                log.logger.debug('Checking folder %s' % d)
                json.dump((fs.ShareInfo(os.path.join(_SHARE,d),c)),jsonfile)
                jsonfile.write('\n')
                log.logger.debug('Done with folder %s' % d)
c.unbind()
