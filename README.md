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

In order to make a really rough distinction with regard to the status of data we use the following status indicators:
  * `preparation`
  * `production`
  * `archive`

### `data_size`

The total size in bytes of the data set.

### `data_amount`

The total amount of files or objects that is part of the data set.

### `data_owner_name`

The name of the primary owner within the organization of the data set.

### `data_owner_id`

The unique identifier of the primary owner within the organization of the data set.

### `data_groups_name`

Array of the names of the groups within the organization that have access to the data set. For example the name of an *Active Directory* (AD) organization group.

### `data_groups_id`

Array of the unique identifiers of the groups within the organization that have access to the data set. For example the GUID of an Active Directory (AD) organization group.

### `data_host`

The individual host or host cluster that is responsible for exposing the data set to users. For example, in case of a file share, the `data_host` equals the fileserver (i.e. `fs-smb-006.ad.naturalis.nl`). The `data_host` can equal `host`, but that is not necessarily the case.

### `data_service_tags`

Array of tags about the service as part of which the data is stored. For example: `nba`, `elasticsearch` and `dev` for data stored on an Elasticsearch node that is part of a development machine for the Netherlands Biodiversity API (NBA) or `fs` and `smb` for the file share example.

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

The storage pool in Ceph:
  * `buckets` (For all data in .rgw*)
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
  "data_id": "7f3201d3-73a8-4be6-b2b9-1223d2e5ee95",
  "data_status": "production",
  "data_size": 13696468,
  "data_amount": 13187,
  "data_owner_name": "Automatisering",
  "data_owner_id": "284f452a-618c-4583-b7c0-dc80dfe6bada",  
  "data_groups_name": [ "Automatisering", "Infra" ],
  "data_groups_id": [ "284f452a-618c-4583-b7c0-dc80dfe6bada", "b3c146a8-2ec1-492e-ad8a-3ab42b9db34c" ],
  "data_host": "fs-smb-006.ad.naturalis.nl",
  "data_service_tags": [ "fs", "smb" ],
  "storage_id": "",
  "storage_path": "smb://fs-smb-006.ad.naturalis.nl/groups/Automatisering",
  "storage_type": "fileshare",
  "storage_location": "primary-cluster-001",
  "storage_pool": "volumes"
}
```

### Local storage

```json
{
  "@timestamp": "2016-10-31T10:45:10.000Z",
  "host": "dt001234.ad.naturalis.nl",
  "data_name": "Scans",
  "data_id": "",
  "data_status": "preparation",
  "data_size": 29632,
  "data_amount": 137,
  "data_owner_name": "",
  "data_owner_id": "",
  "data_groups_name": [],
  "data_groups_id": [],
  "data_host": "dt001234.ad.naturalis.nl",
  "data_service_tags": [],
  "storage_id": "",
  "storage_path": "smb://dt001234.ad.naturalis.nl/C$/Scans",
  "storage_type": "local",
  "storage_location": "local",
  "storage_pool": ""
}
```

### Block storage

```json
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "fs-smb-006.ad.naturalis.nl",
  "data_name": "Dikke schijf",
  "data_id": "",
  "data_status": "production",
  "data_size": 13696468,
  "data_amount": 13187,
  "data_owner_name": "Automatisering",
  "data_owner_id": "284f452a-618c-4583-b7c0-dc80dfe6bada",  
  "data_groups_name": [ "Automatisering", "Infra" ],
  "data_groups_id": [ "284f452a-618c-4583-b7c0-dc80dfe6bada", "b3c146a8-2ec1-492e-ad8a-3ab42b9db34c" ],
  "data_host": "primary-cluster-001",
  "data_service_tags": [ "fs", "smb", "fs-smb-006" ],
  "storage_id": "123223-dfea21-123435-123212",
  "storage_path": "",
  "storage_type": "block",
  "storage_location": "primary-cluster-001",
  "storage_pool": "volumes"
}
```

### Database

```json
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "nba-elasticsearch-dev-003.stack.naturalis.nl",
  "data_name": "Dikke schijf",
  "data_id": "",
  "data_status": "production",
  "data_size": 6566668,
  "data_amount": 13187,
  "data_owner_name": "Software Development",
  "data_owner_id": "bd46682b-73cb-4d96-a752-dc7cc03b02c6",  
  "data_groups_name": [ "Software Development" ],
  "data_groups_id": [ "bd46682b-73cb-4d96-a752-dc7cc03b02c6" ],
  "data_host": "nba-elasticsearch-dev-003.pc.naturalis.nl",
  "data_service_tags": [ "nba", "elasticsearch", "dev", "nba-elasticsearch-dev-003" ],
  "storage_id": "9c9ab56c-f079-4013-913f-20ef7a687749",
  "storage_path": "",
  "storage_type": "database",
  "storage_location": "primary-cluster-001",
  "storage_pool": "volumes"
}
```

### Backup storage

```json
{
  "@timestamp": "2016-10-31T10:39:10.000Z",
  "host": "burp-server-001",
  "data_name": "Dikke schijf",
  "data_id": "",
  "data_status": "production",
  "data_size": 76446548,
  "data_amount": 1858334,
  "data_owner_name": "",
  "data_owner_id": "",
  "data_groups_name": [ "Software Development" ],
  "data_groups_id": [ "bd46682b-73cb-4d96-a752-dc7cc03b02c6" ],
  "data_host": "burp-server-001.bc.naturalis.nl",
  "data_service_tags": [ "fs", "smb", "fs-smb-006" ],
  "storage_id": "9c9ab56c-f079-4013-913f-20ef7a687749",
  "storage_path": "",
  "storage_type": "database",
  "storage_location": "primary-cluster-001",
  "storage_pool": "volumes"
}
```
