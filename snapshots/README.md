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
Created Snapshot 'backup' in filesystem 'prueba1', project 'prueba1', pool 'pool_0'
===============================================================================
Created Snapshot 'backup' in filesystem 'test', project 'test1', pool 'pool_0'
===============================================================================
Failed creating Snapshot 'backup' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesyste
m2/snapshots
===============================================================================
Created Snapshot 'backup1' in filesystem 'prueba1', project 'prueba1', pool 'pool_0'
===============================================================================
Created Snapshot 'backup1' in filesystem 'test', project 'test1', pool 'pool_0'
===============================================================================
Failed creating Snapshot 'backup1' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
Finished in 12 seconds
```

List Snapshots:

```
$./zfssa-snaps.py -s server.yml -f snapshots.csv -l
Snapshot 'backup' in filesystem 'prueba1', project 'prueba1', pool 'pool_0', created at 20170526T19:50:36, space data 0.00GB space unique 0.00GB
===============================================================================
Snapshot 'backup' in filesystem 'test', project 'test1', pool 'pool_0', created at 20170526T19:50:38, space data 0.00GB space unique 0.00GB
===============================================================================
Failed listing snapshot 'backup' in filesystem 'filesystem2', project 'myproject1' and pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
Snapshot 'backup1' in filesystem 'prueba1', project 'prueba1', pool 'pool_0', created at 20170526T19:50:41, space data 0.00GB space unique 0.00GB
===============================================================================
Snapshot 'backup1' in filesystem 'test', project 'test1', pool 'pool_0', created at 20170526T19:50:44, space data 0.00GB space unique 0.00GB
===============================================================================
Failed listing snapshot 'backup1' in filesystem 'filesystem2', project 'myproject1' and pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
===============================================================================
Finished in 7 seconds
```

Delete Snapshots:

```text
./zfssa-snaps.py -s server.yml -f snapshots.csv -d
###############################################################################
Deleting snapshots
###############################################################################
Deleted Snapshot 'backup' in filesystem 'prueba1', project 'prueba1', pool 'prueba1'
===============================================================================
Deleted Snapshot 'backup' in filesystem 'test', project 'test1', pool 'test1'
===============================================================================
Failed deleting snapshot 'backup' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup
===============================================================================
Deleted Snapshot 'backup1' in filesystem 'prueba1', project 'prueba1', pool 'prueba1'
===============================================================================
Deleted Snapshot 'backup1' in filesystem 'test', project 'test1', pool 'test1'
===============================================================================
Failed deleting snapshot 'backup1' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots/backup1
===============================================================================
Finished in 57 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating snapshots with progress option:

```text
./zfssa-snaps.py -s server.yml -f snapshots.csv -c -p
Processing |#####################           | 4/6 - remain: 2 - 66.7% - 6s
```

Output file example.

```
cat snapshots_output.log
2017-05-26 20:03:15,385 - snapshots - INFO - Created Snapshot 'backup' in filesystem 'prueba1', project 'prueba1', pool 'pool_0'
2017-05-26 20:03:18,063 - snapshots - INFO - Created Snapshot 'backup' in filesystem 'test', project 'test1', pool 'pool_0'
2017-05-26 20:03:19,183 - snapshots - WARNING - Failed creating Snapshot 'backup' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
2017-05-26 20:03:22,486 - snapshots - INFO - Created Snapshot 'backup1' in filesystem 'prueba1', project 'prueba1', pool 'pool_0'
2017-05-26 20:03:26,263 - snapshots - INFO - Created Snapshot 'backup1' in filesystem 'test', project 'test1', pool 'pool_0'
2017-05-26 20:03:27,894 - snapshots - WARNING - Failed creating Snapshot 'backup1' in filesystem 'filesystem2', project 'myproject1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/myproject1/filesystems/filesystem2/snapshots
```