#!/usr/bin/python2.7

# Script to get stats about block storage managed by OpenStack Cinder

import json
import sys

from lib.keystone import KeyStone
from lib.nova import Nova
from lib.cinder import Cinder
from utils import log
from utils import config
from keystoneclient.openstack.common.apiclient import exceptions as ksexc

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

"""
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "fs-smb-006.ad.naturalis.nl",
  "data_set": { "name": "Dikke schijf", "id": "" },
  "data_status": "production",
  "data_size": 13696468,
  "data_amount": 13187,
  "data_owner": { "name": "Automatisering", "id": "284f452a-618c-4583-b7c0-dc80dfe6bada" },
  "data_groups": [
    { "name": "Automatisering", "id": "284f452a-618c-4583-b7c0-dc80dfe6bada" },
    { "name": "Infra", "id": "b3c146a8-2ec1-492e-ad8a-3ab42b9db34c" }
  ],
  "data_host": "primary-cluster-001",
  "data_service_tags": [ "fs", "smb", "fs-smb-006" ],
  "storage_id": "123223-dfea21-123435-123212",
  "storage_path": "",
  "storage_type": "block",
  "storage_location": "primary-cluster-001",
  "storage_pool": "volumes"
}
"""

keystone = KeyStone(auth_url_no_ssl, ks_username, ks_password,
                    project_name, ca_bundle)
for p in keystone.list_projects():
    if p['id'] in project_ids_skip:
        log.logger.debug("Skipped: excluding volumes in project %s with "
                         "id %s" % (p['name'], p['id']))
    else:
        log.logger.debug("Checking volumes in project %s with id %s"
                         % (p['name'], p['id']))
        cinder = Cinder(auth_url_no_ssl, ks_username, ks_password,
                        project_name, ca_bundle, p['id'])
        nova = Nova(auth_url_no_ssl, ks_username, ks_password,
                    p['id'], ca_bundle)

        try:
            volume_info = cinder.get_volume_info()
            for v_i in volume_info:
                v_i['storage_id'] = v_i['id']
                v_i['data_owner'] = { "name" :  p['name'] , "id" : p['id'] }
                v_i['data_groups'] = { "name" :  p['name'] , "id" : p['id'] }
                v_i['data_set'] = { "name" : v_i['name'], "id" : v_i['id'] }
                v_i['storage_type'] = 'block'
                v_i['storage_path'] = ''
                v_i['data_amount'] = ''
                v_i['data_size'] = v_i['size']
                v_i['data_status'] = 'production'
                v_i['storage_location'] = 'primary-cluster-001'
                v_i['data_host'] = 'primary-cluster-001'
                v_i['storage_pool'] = 'volumes'

                if not v_i['attached_to_id'] == '':
                    v_i['host'] = nova.get_server_name_from_id(
                                              v_i['attached_to_id'])
                else:
                    v_i['host'] = 'Not Attached'

                # cleanup
                fields = ['attached_to_id', 'status', 'name', 'id']
                for field in fields:
                    del v_i[field]

                            
                with open(json_location, 'a') as jsonfile:
                    log.logger.debug('Writing json volume: %s' %
                                     v_i['data_set']['name'])
                    json.dump(v_i, jsonfile)
                    jsonfile.write('\n')
        except ksexc.Unauthorized:
            log.logger.debug("Unauthorized: excluding volumes in project "
                             "%s with id %s" % (p['name'], p['id']))
        except:
            log.logger.debug("Unexpected error: %s", sys.exc_info()[0])
