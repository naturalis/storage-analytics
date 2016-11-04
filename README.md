# Data storage analytics

The idea is to monitor data storage by collecting (starting on a daily basis) basic statistics about fileshares, volumes and other forms of data storage in use at Naturalis. Since Naturalis makes extensive use of Elasticsearch and Kibana, we'll be sending JSON data to our existing Elasticsearch analytics cluster.

## Format

### `@timestamp`

Simple: the timestamp of the log message.

### `host`

The full qualified domain name of the host from which the statistics is logged. Not necessarily the host on which data is stored.

### `data_name`

The name of the specific set of data.

### `data_id`

An unique identifier for the specific set of data. For example the GUID of the resource group in Active Directory.

### `data_status`

In order to make a really rough distinction with regard to the status of data we use three basic statuses:
  * `preparation`
  * `production`
  * `archive`

### `data_size`

The total size in bytes of the data set.

### `data_amount`

The total amount of files or objects that is part of the data set.

### `data_owner`

The primary owner within the organization of the data set.

### `data_groups_name`

Array of the names of the groups within the organization that have access to the data set. For example the name of an *Active Directory* (AD) organization group.

### `data_groups_id`

Array of the unique identifiers of the groups within the organization that have access to the data set. For example the GUID of an Active Directory (AD) organization group.

### `data_service`

The service as part of which the data is stored. For example: `col` for Catalogue of Life.

### `storage_id`

The unique identifier for the specific storage location. For example the UUID of a volume in OpenStack.

### `storage_path`

The path to the location where the data set is stored. For example, in case of a file share; `smb://fs-smb-006.ad.naturalis.nl/groups/Automatisering`

### `storage_type`

Storage types refer to the type of data storage on which the data set is stored. We distinguish the following storage types:
  * `local` (A directory on local storage of a physical machine)
  * `fileshare` (A file share or network share. Typically a SMB/CIFS share)
  * `block` (Block storage, typically volumes in OpenStack)
  * `object` (Object storage, typically object store in OpenStack / Ceph)
  * `database` (Any data that is stored in some form of database, either SQL or NoSQL)
  * `web` (Data that is stored in some form of public cloud storage, for example Google Drive)
  * `backup` (Data that is backupped by a dedicated backup program, i.e. Burp)

### `storage_location`

In order to aggregate statistics based on the storage location we use this format:
  * `local` (Generic term for storage on 'local' desktops, workstations etc.)
  * `primary-cluster-001` (We currently have one, but might get more in the future)
  * `backup-cluster-001` (We currently have one, but might get more in the future)
  * `google-drive` (Just an example of a specific external data store)
  * `external` (Generic term for storage on 'external' systems)

### `storage_pool`

*Optional*. For data stored on Ceph we add the specific pool as well (`ceph_pool`):
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
  "data_name": "AUT",
  "data_id": "",
  "data_status": "production",
  "data_size": 13696468,
  "data_amount": 13187,
  "data_owner": "Automatisering",
  "data_groups_name": [
     "Automatisering",
     "Infra"
  ]
  "data_groups_id": [
    "3435-1254-1312-3223",
    "5435-6254-4568-9253"
  ]
  "data_service": "",
  "storage_id": "",
  "storage_path": "smb://fs-smb-006.ad.naturalis.nl/groups/Automatisering",
  "storage_type": "fileshare",
  "storage_location": "primary-cluster-001",
  "storage_pool": "data"
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

### Database

```json
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "fs-smb-006.ad.naturalis.nl",
  "name": "AUT",
  "id": "",
  "storage_type": "database",
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
