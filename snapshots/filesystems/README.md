zfssa_fs_snaps.py
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
./zfssa_fs_snaps.py -h
usage: zfssa_fs_snaps.py [-h] -s SERVER -f FILE [-p] [-c | -d | -l]

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
$./zfssa_fs_snaps.py -s server.yml -f snapshots.csv -c
###############################################################################
Creating snapshots
###############################################################################
CREATE - SUCCESS - snapshot 'backup' filesystem 'fs1' project 'project1' pool 'pool_0'
===============================================================================
CREATE - SUCCESS - snapshot 'backup' filesystem 'fs2' project 'project1' pool 'pool_0'
===============================================================================
CREATE - FAIL - snapshot 'backup' filesystem 'nofs' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
===============================================================================
CREATE - FAIL - snapshot 'backup' filesystem 'nofs' project 'noproject' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
===============================================================================
CREATE - SUCCESS - snapshot 'backup' filesystem 'fs3' project 'project1' pool 'pool_0'
===============================================================================
Finished in 8 seconds
```

List Snapshots:

```text
$./zfssa_fs_snaps.py -s server.yml -f snapshots.csv -l
###############################################################################
Listing snapshots
###############################################################################
LIST - PRESENT - snapshot 'backup' filesystem 'fs1' project 'project1' pool 'pool_0' created_at '20170618T17:12:46' space_data '31.00KB' space_unique '0.00'
===============================================================================
LIST - PRESENT - snapshot 'backup' filesystem 'fs2' project 'project1' pool 'pool_0' created_at '20170618T17:12:48' space_data '31.00KB' space_unique '0.00'
===============================================================================
LIST - FAIL - snapshot 'backup' filesystem 'nofs' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
===============================================================================
LIST - FAIL - snapshot 'backup' filesystem 'nofs' project 'noproject' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
===============================================================================
LIST - PRESENT - snapshot 'backup' filesystem 'fs3' project 'project1' pool 'pool_0' created_at '20170618T17:12:52' space_data '31.00KB' space_unique '0.00'
===============================================================================
Finished in 1 seconds
```

Delete Snapshots:

```text
./zfssa_fs_snaps.py -s server.yml -f snapshots.csv -d
###############################################################################
Deleting snapshots
###############################################################################
DELETE - SUCCESS - snapshot 'backup' filesystem 'fs1' project 'project1' pool 'pool_0'
===============================================================================
DELETE - SUCCESS - snapshot 'backup' filesystem 'fs2' project 'project1' pool 'pool_0'
===============================================================================
DELETE - FAIL - snapshot 'backup' filesystem 'nofs' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots/backup
===============================================================================
DELETE - FAIL - snapshot 'backup' filesystem 'nofs' project 'noproject' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots/backup
===============================================================================
DELETE - SUCCESS - snapshot 'backup' filesystem 'fs3' project 'project1' pool 'pool_0'
===============================================================================
Finished in 20 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating snapshots with progress option:

```text
./zfssa_fs_snaps.py -s server.yml -f snapshots.csv -c -p
Processing |#####################           | 4/5 - remain: 2 - 80.0% - 6s
```

Output file example.

```text
cat snapshots_output.log
2017-06-18 17:17:17,805 - snapshots - INFO - CREATE - SUCCESS - snapshot 'backup' filesystem 'fs1' project 'project1' pool 'pool_0'
2017-06-18 17:17:19,614 - snapshots - INFO - CREATE - SUCCESS - snapshot 'backup' filesystem 'fs2' project 'project1' pool 'pool_0'
2017-06-18 17:17:19,816 - snapshots - WARNING - CREATE - FAIL - snapshot 'backup' filesystem 'nofs' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/filesystems/nofs/snapshots
2017-06-18 17:17:21,457 - snapshots - WARNING - CREATE - FAIL - snapshot 'backup' filesystem 'nofs' project 'noproject' pool 'pool_0' - Error 404 Client Error: NotFound for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/noproject/filesystems/nofs/snapshots
2017-06-18 17:17:23,266 - snapshots - INFO - CREATE - SUCCESS - snapshot 'backup' filesystem 'fs3' project 'project1' pool 'pool_0'
```
