#!/usr/bin/python2.7

# Script to get stats about block storage managed by OpenStack Cinder

from lib.keystone import KeyStone
from lib import nova
from lib import cinder
from lib import log
from lib import config


#### Get settings from config
auth_url = 'https://' + config.get('admin_endpoint_ip') + ':5000/v3'
auth_url_v2 = 'https://' + config.get('admin_endpoint_ip') + ':5000/v2.0'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
ca_bundle = config.get('ca_bundle_file')

### End Settings
### start API's
keystone = KeyStone(auth_url,ks_username,ks_password,project_name,ca_bundle)
#nova = Nova(auth_url_v2,ks_username,ks_password,project_name,ca_bundle)
#cinder = Cinder(auth_url_v2,ks_username,ks_password,project_name,ca_bundle)
