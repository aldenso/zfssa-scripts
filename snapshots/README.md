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

```text
./zfssa-snaps.py -h
usage: zfssa-snaps.py [-h] -s SERVER -f FILE [-p] [-c | -d | -l]

Script to handle snapshots in ZFS Storage Appliance

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -f FILE, --file FILE  Snapshots file (CSV)
  -p, --progress        progress bar and logging to file
  -c, --create          Create Snapshots specified in csv file
  -d, --delete          Delete Snapshots specified in csv file
  -l, --list            List/Check Snapshots specified in csv file
```

Create Snapshots.

```text
$./zfssa-snaps.py -s server.yml -f snapshots.csv -c
###############################################################################
Creating snapshots from snapshots.csv
###############################################################################
CREATE - SUCCESS - Snapshot 'backup', filesystem 'prueba1', project 'prueba1', pool 'pool_0'
===============================================================================
CREATE - SUCCESS - Snapshot 'backup', filesystem 'test', project 'test1', pool 'pool_0'
===============================================================================
CREATE - FAIL - Snapshot 'backup', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
CREATE - SUCCESS - Snapshot 'backup1', filesystem 'prueba1', project 'prueba1', pool 'pool_0'
===============================================================================
CREATE - SUCCESS - Snapshot 'backup1', filesystem 'test', project 'test1', pool 'pool_0'
===============================================================================
CREATE - FAIL - Snapshot 'backup1', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
Finished in 11 seconds
```

List Snapshots:

```text
$./zfssa-snaps.py -s server.yml -f snapshots.csv -l
###############################################################################
Listing snapshots
###############################################################################
LIST - PRESENT - Snapshot 'backup', filesystem 'prueba1', project 'prueba1', pool 'pool_0' - Message created at 20170527T17:29:16, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - PRESENT - Snapshot 'backup', filesystem 'test', project 'test1', pool 'pool_0' - Message created at 20170527T17:29:20, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - FAIL - Snapshot 'backup', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
LIST - PRESENT - Snapshot 'backup1', filesystem 'prueba1', project 'prueba1', pool 'pool_0' - Message created at 20170527T17:29:22, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - PRESENT - Snapshot 'backup1', filesystem 'test', project 'test1', pool 'pool_0' - Message created at 20170527T17:29:26, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - FAIL - Snapshot 'backup1', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
Finished in 0 seconds
```

Delete Snapshots:

```text
./zfssa-snaps.py -s server.yml -f snapshots.csv -d
###############################################################################
Deleting snapshots
###############################################################################
DELETE - SUCCESS - Snapshot 'backup', filesystem 'prueba1', project 'prueba1', pool 'prueba1'
===============================================================================
DELETE - SUCCESS - Snapshot 'backup', filesystem 'test', project 'test1', pool 'test1'
===============================================================================
DELETE - FAIL - Snapshot 'backup', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup
===============================================================================
DELETE - SUCCESS - Snapshot 'backup1', filesystem 'prueba1', project 'prueba1', pool 'prueba1'
===============================================================================
DELETE - SUCCESS - Snapshot 'backup1', filesystem 'test', project 'test1', pool 'test1'
===============================================================================
DELETE - FAIL - Snapshot 'backup1', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup1
===============================================================================
Finished in 35 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating snapshots with progress option:

```text
./zfssa-snaps.py -s server.yml -f snapshots.csv -c -p
Processing |#####################           | 4/6 - remain: 2 - 66.7% - 6s
```

Output file example.

```text
cat snapshots_output.log
2017-05-27 17:32:09,286 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup', filesystem 'prueba1', project 'prueba1', pool 'pool_0'
2017-05-27 17:32:11,975 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup', filesystem 'test', project 'test1', pool 'pool_0'
2017-05-27 17:32:13,516 - snapshots - WARNING - CREATE - FAIL - Snapshot 'backup', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
2017-05-27 17:32:15,127 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup1', filesystem 'prueba1', project 'prueba1', pool 'pool_0'
2017-05-27 17:32:18,692 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup1', filesystem 'test', project 'test1', pool 'pool_0'
2017-05-27 17:32:19,907 - snapshots - WARNING - CREATE - FAIL - Snapshot 'backup1', filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
```
