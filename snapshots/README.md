zfssa-snaps.py
==============

Script to create, delete and list snapshots in filesystems.

config or server file must be yaml.

Example

```yml
ip: 192.168.56.150
username: root
password: password
```

Snapshots file must be csv, and columns must be in the next order:

	pool,project,filesystem,snapname

Example:

```text
pool_0,prueba1,prueba1,backup
pool_0,test1,test,backup
pool_0,myproject1,filesystem2,backup
pool_0,prueba1,prueba1,backup1
```

Usage:

```
./zfssa-snaps.py -h
usage: zfssa-snaps.py [-h] -s SERVER -f FILE [-c | -d | -l]

Script to handle snapshots in ZFS Storage Appliance

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -f FILE, --file FILE  Snapshots file (CSV)
  -c, --create          Create Snapshots specified in csv file
  -d, --delete          Delete Snapshots specified in csv file
  -l, --list            List/Check Snapshots specified in csv file
```


Create Snapshots.

```
$./zfssa-snaps.py -s server.yml -f snapshots.csv -c
###############################################################################
Creating snapshots from snapshots.csv
###############################################################################
Creating Snapshot: 'backup'
pool: pool_0, project: prueba1, filesystem: prueba1
+++ SUCCESS +++
===============================================================================
Creating Snapshot: 'backup'
pool: pool_0, project: test1, filesystem: test
+++ SUCCESS +++
===============================================================================
Creating Snapshot: 'backup'
pool: pool_0, project: myproject1, filesystem: filesystem2
message: the requested item was not found (EAK_ZFS_NOENT: {txtid: "AKTXT_NAS_NOENT", args: ["myproject1/filesystem2"]})
Error: 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
--- FAILED ---
===============================================================================
Creating Snapshot: 'backup1'
pool: pool_0, project: prueba1, filesystem: prueba1
+++ SUCCESS +++
===============================================================================
Creating Snapshot: 'backup1'
pool: pool_0, project: test1, filesystem: test
+++ SUCCESS +++
===============================================================================
Creating Snapshot: 'backup1'
pool: pool_0, project: myproject1, filesystem: filesystem2
message: the requested item was not found (EAK_ZFS_NOENT: {txtid: "AKTXT_NAS_NOENT", args: ["myproject1/filesystem2"]})
Error: 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
--- FAILED ---
===============================================================================
Finished in 12 seconds
```

List Snapshots:

```
$./zfssa-snaps.py -s server.yml -f snapshots.csv -l
###############################################################################
Listing snapshots
###############################################################################
Snapshot: backup, created at: 20170130T23:45:00
pool: pool_0, project: prueba1, filesystem: prueba1
space data: 0.00GB space unique: 0.00GB
===============================================================================
Snapshot: backup, created at: 20170130T23:45:04
pool: pool_0, project: test1, filesystem: test
space data: 0.00GB space unique: 0.00GB
===============================================================================
Failed request to check snapshot: 'backup'
share 'filesystem2' in project 'myproject1' and pool 'pool_0' doesn't exists.
===============================================================================
Snapshot: backup1, created at: 20170130T23:45:06
pool: pool_0, project: prueba1, filesystem: prueba1
space data: 0.00GB space unique: 0.00GB
===============================================================================
Snapshot: backup1, created at: 20170130T23:45:10
pool: pool_0, project: test1, filesystem: test
space data: 0.00GB space unique: 0.00GB
===============================================================================
Failed request to check snapshot: 'backup1'
share 'filesystem2' in project 'myproject1' and pool 'pool_0' doesn't exists.
===============================================================================
Finished in 2 seconds
```

Delete Snapshots:

```
./zfssa-snaps.py -s server.yml -f snapshots.csv -d
###############################################################################
Deleting snapshots from snapshots.csv
###############################################################################
Deleting Snapshot: 'backup'
pool: pool_0, project: prueba1, filesystem: prueba1
+++ SUCCESS +++
===============================================================================
Deleting Snapshot: 'backup'
pool: pool_0, project: test1, filesystem: test
+++ SUCCESS +++
===============================================================================
Deleting Snapshot: 'backup'
pool: pool_0, project: myproject1, filesystem: filesystem2
Error: 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup
--- FAILED ---
===============================================================================
Deleting Snapshot: 'backup1'
pool: pool_0, project: prueba1, filesystem: prueba1
+++ SUCCESS +++
===============================================================================
Deleting Snapshot: 'backup1'
pool: pool_0, project: test1, filesystem: test
+++ SUCCESS +++
===============================================================================
Deleting Snapshot: 'backup1'
pool: pool_0, project: myproject1, filesystem: filesystem2
Error: 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup1
--- FAILED ---
===============================================================================
Finished in 34 seconds
```