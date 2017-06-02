zfssa-snaps.py
==============

Script to create, delete and list snapshots in filesystems for ZFS Storage Appliance (tested on OS8.6 and OS8.7).

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
pool_0,project1,fs1,backup
pool_0,project1,fs2,backup
pool_0,project1,nofs,backup
pool_0,noproject,nofs,backup
pool_0,project1,fs3,backup
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
Creating snapshots from .\snapshots.csv
###############################################################################
CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs1', project 'project1', pool 'pool_0'
===============================================================================
CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs2', project 'project1', pool 'pool_0'
===============================================================================
CREATE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'project1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/s
torage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
===============================================================================
CREATE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'noproject', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/
storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
===============================================================================
CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs3', project 'project1', pool 'pool_0'
===============================================================================
Finished in 10 seconds
```

List Snapshots:

```text
$./zfssa-snaps.py -s server.yml -f snapshots.csv -l
###############################################################################
Listing snapshots
###############################################################################
LIST - PRESENT - Snapshot 'backup', filesystem 'fs1', project 'project1', pool 'pool_0' - Message created at 20170602T18:58:03, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - PRESENT - Snapshot 'backup', filesystem 'fs2', project 'project1', pool 'pool_0' - Message created at 20170602T18:58:07, space data 0.00GB space unique 0.00GB
===============================================================================
LIST - FAIL - Snapshot 'backup', filesystem 'nofs', project 'project1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
===============================================================================
LIST - FAIL - Snapshot 'backup', filesystem 'nofs', project 'noproject', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
===============================================================================
LIST - PRESENT - Snapshot 'backup', filesystem 'fs3', project 'project1', pool 'pool_0' - Message created at 20170602T18:58:12, space data 0.00GB space unique 0.00GB
===============================================================================
Finished in 2 seconds
```

Delete Snapshots:

```text
./zfssa-snaps.py -s server.yml -f snapshots.csv -d
###############################################################################
Deleting snapshots
###############################################################################
DELETE - SUCCESS - Snapshot 'backup', filesystem 'fs1', project 'project1', pool 'project1'
===============================================================================
DELETE - SUCCESS - Snapshot 'backup', filesystem 'fs2', project 'project1', pool 'project1'
===============================================================================
DELETE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'project1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https
://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots/backup
===============================================================================
DELETE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'noproject', pool 'pool_0' - Error 404 Client Error: Not Found for url: http
s://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots/backup
===============================================================================
DELETE - SUCCESS - Snapshot 'backup', filesystem 'fs3', project 'project1', pool 'project1'
===============================================================================
Finished in 31 seconds
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
2017-06-02 19:02:14,644 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs1', project 'project1', pool 'pool_0'
2017-06-02 19:02:20,207 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs2', project 'project1', pool 'pool_0'
2017-06-02 19:02:20,473 - snapshots - WARNING - CREATE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'project1', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
2017-06-02 19:02:20,677 - snapshots - WARNING - CREATE - FAIL - Snapshot 'backup', filesystem 'nofs', project 'noproject', pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
2017-06-02 19:02:23,642 - snapshots - INFO - CREATE - SUCCESS - Snapshot 'backup', filesystem 'fs3', project 'project1', pool 'pool_0'
```
