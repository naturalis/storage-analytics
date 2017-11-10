from __future__ import print_function
import httplib2
import os
from datetime import datetime, timedelta
import socket
import re
import json

from utils import config
from utils import log

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Follow these instructions to get credentials:
# https://developers.google.com/admin-sdk/reports/v1/guides/prerequisites
# https://developers.google.com/admin-sdk/reports/v1/quickstart/python

def get_credentials():
    """Gets valid user credentials from storage.

    Returns:
        Credentials, the obtained credential.
    """
    try:
        credential_path = config.get('google_credentials', 'gsuite')
        store = Storage(credential_path)
        credentials = store.get()
        if credentials.invalid:
            log.logger.error('The provided credentials were invalid.')
        else:
            return credentials
    except Exception as e:
        log.logger.error('Something went wrong with the credentials.')

def main():
    json_location = config.get('output_file', 'gsuite')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'reports_v1', http=http)
    d = datetime.today() - timedelta(days=4)
    ds = d.strftime("%Y-%m-%d")
    di = d.isoformat()
    p = ("accounts:total_quota_in_mb,"
         "accounts:used_quota_in_mb,"
         "accounts:gmail_used_quota_in_mb,"
         "accounts:drive_used_quota_in_mb,"
         "accounts:gplus_photos_used_quota_in_mb")
    results = service.userUsageReport().get(date=ds,
                                           userKey='all',
                                           parameters=p).execute()
    token = results.get('nextPageToken', None)
    reports = results.get('usageReports', [])
    while token is not None:
        results = service.userUsageReport().get(date=ds,
                                                pageToken=token,
                                                userKey='all',
                                                parameters=p).execute()
        reports += results.get('usageReports', [])
        token = results.get('nextPageToken', None)
    with open(json_location, 'a') as jsonfile:
        for user in reports:
            json_dict = {'timestamp': di,
                     'host': socket.getfqdn(),
                     'data_owner': {'name': user[u'entity'][u'userEmail'],
                                    'id': user[u'entity'][u'profileId']},
                     'data_set': {},
                     'storage_type': 'web',
                     'storage_location': 'google',
                     'data_status': 'production',
                     'fields': {'type': 'storage'}
                     }
            for i in user[u'parameters']:
                if i[u'name'] == u'accounts:gmail_used_quota_in_mb':
                    json_dict['data_set']['name'] = re.sub('@.*',
                                                   '@mail.google.com',
                                                   user[u'entity'][u'userEmail'])
                    json_dict['data_service_tags'] = ['gsuite', 'gmail',
                                                      'personal']
                    json_dict['data_size'] = int(i[u'intValue'])*1024**2
                    json.dump(json_dict, jsonfile)
                    jsonfile.write('\n')
                elif i[u'name'] == u'accounts:drive_used_quota_in_mb':
                    json_dict['data_set']['name'] = re.sub('@.*',
                                                   '@drive.google.com',
                                                   user[u'entity'][u'userEmail'])
                    json_dict['data_service_tags'] = ['gsuite', 'drive',
                                                      'mydrive', 'personal']
                    json_dict['data_size'] = int(i[u'intValue'])*1024**2
                    json.dump(json_dict, jsonfile)
                    jsonfile.write('\n')
                elif i[u'name'] == u'accounts:gplus_photos_used_quota_in_mb':
                    json_dict['data_set']['name'] = re.sub('@.*',
                                                   '@photos.google.com',
                                                   user[u'entity'][u'userEmail'])
                    json_dict['data_service_tags'] = ['gsuite', 'photos',
                                                      'personal']
                    json_dict['data_size'] = int(i[u'intValue'])*1024**2
                    json.dump(json_dict, jsonfile)
                    jsonfile.write('\n')

if __name__ == '__main__':
    main()
