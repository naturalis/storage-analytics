[Default]
admin_endpoint_ip = 127.0.0.1
os_username = admin
os_password = secret
os_project_name = admin
ad_user = your_ad_user
ad_password = your_ad_password
ad_domain = SHORT_DOMAIN_NAME
account_mail_to = info@info.com
ad_host = 127.0.0.1
ks_ad_group_sync_id = ae41c863c3474201957e330885deda5e
elastic_host = localhost
elastic_port = 9200

[fileshare]
share_folder = /data
output_file = /var/log/storage-analytics.json

[block_storage_cinder]
output_file = /tmp/volumeinfo.json
storage_location = primary-cluster-001

[backup-burp-linux]
output_file = /var/log/storage-analytics.json

[infra_stats]
google_credentials = ./google-authentication.json
cmdb_key = 5GmAJj9iiya4A69P31g8HhBPc6UdpB7MhY1mWWOeUwQI
factsheet_key = R2MU5ZVjakX62vQ111VDd3x6du1pEvbMEVNXbOOTTYhI
output_file = /tmp/infra-stats.json
