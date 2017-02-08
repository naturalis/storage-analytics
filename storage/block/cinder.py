#!/usr/bin/python2.7

# Script to get stats about block storage managed by OpenStack Cinder

import json

from lib.keystone import KeyStone
from lib.nova import Nova
from lib.cinder import Cinder
from utils import log
from utils import config


# Get settings from config
auth_url = 'https://' + config.get('admin_endpoint_ip') + ':5000/v3'
auth_url_no_ssl = 'http://' + config.get('admin_endpoint_ip') + ':5000/v3'
auth_url_v2 = 'http://' + config.get('admin_endpoint_ip') + ':5000/v2.0'
ks_username = config.get('os_username')
ks_password = config.get('os_password')
project_name = config.get('os_project_name')
ca_bundle = config.get('ca_bundle_file')
json_location = config.get('output_file', 'block_storage_cinder')
project_ids_skip = ['baf09a7e28bf448092707fa9917f8aae',
                    'b60f923463e04a4bb1858388aed6239f']
# End Settings
# start API's


keystone = KeyStone(auth_url_no_ssl, ks_username, ks_password,
                    project_name, ca_bundle)
for p in keystone.list_projects():
    if p['id'] in project_ids_skip:
        log.logger.debug('Excluding volumes in project %s with \
        id %s' % (p['name'], p['id']))
    else:
        log.logger.debug('Checking volumes in project %s with \
        id %s' % (p['name'], p['id']))
        cinder = Cinder(auth_url_no_ssl, ks_username, ks_password,
                        project_name, ca_bundle, p['id'])
        nova = Nova(auth_url_no_ssl, ks_username, ks_password,
                    p['id'], ca_bundle)

        try:
            volume_info = cinder.get_volume_info()
            for v_i in volume_info:
                v_i['project_id'] = p['id']
                v_i['project_name'] = p['name']
                v_i['storage_type'] = 'block'
                v_i['storage_location'] = 'primary-cluster-001'
                v_i['storage_pool'] = 'volumes'

                if not v_i['attached_to_id'] == '':
                    v_i['attached_to_name'] = nova.get_server_name_from_id(
                                              v_i['attached_to_id'])
                else:
                    v_i['attached_to_name'] = ''

                with open(json_location, 'a') as jsonfile:
                    log.logger.debug('Writing json volume: %s' % v_i['name'])
                    json.dump(v_i, jsonfile)
                    jsonfile.write('\n')
        except keystoneclient.openstack.common.apiclient.exceptions.Unauthorized:
            log.logger.debuglog.logger.debug('Excluding volumes in project \
            %s with id %s' % (p['name'], p['id']))
        except:
            log.logger.debuglog.logger.debug('Unexpected error: %s',
                                             sys.exc_info()[0])
