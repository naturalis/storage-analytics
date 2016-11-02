# Data storage analytics

The idea is to monitor data storage by collecting (starting on a daily basis) basic statistics about fileshares, volumes and other forms of data storage in use at Naturalis. Since Naturalis makes extensive use of Elasticsearch and Kibana, we'll be sending JSON data to our existing Elasticsearch analytics cluster.

## Format



### `storage_type`

Storage types refer to the kind of data is offered to (groups of) users (either humans or machines). We distinguish the following storage types:
  * `local storage`
  * `fileshare`
  * `block storage`
  * `object storage`
  * `web storage`
  * `backup storage`

### `data_lifecycle_stage`

In order te make a really rough distinction with regard to the data life cycle we use three basic stages (`data_lifecycle_stage`):
  * `preparation`
  * `production`
  * `archive`

### `storage_location`

In order to aggregate statistics based on the storage location we use this format:
  * `local` (Generic term for storage on 'local' desktops, workstations etc.)
  * `primary-cluster-001` (We currently have one, but might get more in the future)
  * `backup-cluster-001` (We currently have one, but might get more in the future)
  * `google-drive` (Just an example of a specific external data store)
  * `external` (Generic term for storage on 'external' systems)

### `ceph_pool`

For data stored on Ceph we add the specific pool as well (`ceph_pool`):
  * `data`
  * `compute`
  * `images`
  * `volumes`

## Examples

### Fileshare

```json
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "fs-smb-006.ad.naturalis.nl",
  "name": "AUT",
  "id": "",
  "storage_type": "fileshare",
  "storage_location": "primary-cluster-001",
  "data_lifecycle_stage": "production",
  "total_size": 13696468,
  "total_files": 13187,
  "path": "smb://fs-smb-006.ad.naturalis.nl/groups/Automatisering",
  "ceph_pool": "data",
  "owner": "Automatisering",
  "ad_groups": [
      {
        "id": "2323-2323-1212-4223",
        "name": "Automatisering"
      },
  ]
    "user":
      {
        "id": "3435-1254-1312-3223",
        "name": "natsysd"
      }
  ]
}
```

### Local storage

```json
{
  "@timestamp": "2016-10-31T10:45:10.000Z",
  "host": "dt001234.ad.naturalis.nl",
  "name": "Scans",
  "storage_type":"local storage",
  "data_lifecycle_stage": "preparation",
  "storage_location": "local",
  "path": "smb://dt001234.ad.naturalis.nl/C$/Scans",
  "size": 13696468,
  "files": 13187,
  "authorizations": [
    "group":
      {
        "id": "2323-2323-1212-4223",
        "name": "Automatisering"
      }
    "user":
      {
        "id": "3435-1254-1312-3223",
        "name": "natsysd"
      }
  ]
}
```

### Block storage

```json
{
  "@timestamp": "2016-10-31T10:45:10.000Z",
  "host": "dt001234.ad.naturalis.nl",
  "name": "Scans",
  "storage_type": "block storage",
  "data_lifecycle_stage": "production",
  "storage_location": "primary-cluster-001",
  "ceph_pool": "volumes",
  "size": 13696468,
  "volume_id": "123223-dfea21-123435-123212",
  "authorizations": [
    "group":
      {
        "id": "2323-2323-1212-4223",
        "name": "Automatisering"
      }
    "user":
      {
        "id": "3435-1254-1312-3223",
        "name": "natsysd"
      }
  ]
}
```

```json
{
  "@timestamp": "2016-10-31T10:45:10.000Z",
  "host": "dt001234.ad.naturalis.nl",
  "name": "Dikke schijf",
  "id": "c03012-1232dfe-1212457-ba03241",
  "storage": {
    "type": "local storage",
    "stage": "preparation",
    "place": "primary",
    "pool": "nonshared"
  },
  "path": "",
  "size": 13696468,
  "files": 1,
  "authorizations": [
    "group":
      {
        "id": "2323-2323-1212-4223",
        "name": "Automatisering"
      }
    "user":
      {
        "id": "3435-1254-1312-3223",
        "name": "natsysd"
      }
  ]
}
```
### Backup storage

```json
{
  "@timestamp": "2016-10-31T10:45:10.000Z",
  "host": "dt001234.ad.naturalis.nl",
  "name": "Dikke schijf",
  "id": "c03012-1232dfe-1212457-ba03241",
  "storage": {
    "type": "backup storage",
    "stage": "production",
    "place": "backup-cluster-001",
    "pool": "backups"
  },
  "path": "",
  "size": 13696468,
  "files": 1,
  "authorizations": [
    "group":
      {
        "id": "2323-2323-1212-4223",
        "name": "Automatisering"
      }
    "user":
      {
        "id": "3435-1254-1312-3223",
        "name": "natsysd"
      }
  ]
}
```
