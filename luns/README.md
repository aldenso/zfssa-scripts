zfssa-luns.py
==============

Script to create, delete and list luns.

config or server file must be yaml.

Example

```yml
ip: 192.168.56.150
username: root
password: password
```

Luns file must be csv, and columns (12) must be in the next order for lun **creation** or **listing**:

```text
pool,project,lun,size,size_unit,blocksize,thin,targetgroup,initiatorgroup,compression,dedup,nodestroy
```

Example:

```text
#pool(str),project(str),lun(str),size(int),size_unit(str),blocksize(str),thin(bool),targetgrp(str),initiatorgrp(str),compression(str),dedup(bool),nodestroy(bool)
pool_0,project1,lun01,1,gb,128k,True,default,cluster-test,gzip,False,False
pool_0,project1,lun02,2,gb,64k,True,default,cluster-test,off,False,True
pool_0,project1,lun03,1024,MB,8k,False,default,default,off,False,False
pool_0,project1,lun04,256,MB,512k,False,default,vmcluster,off,False,False
```

**Note**: don't remove the header from the file.

For lun **deletion** or **listing**, the file must be csv and columns (3) must be in the next order:

```text
pool,project,lun
```

Example:

```text
#pool(str),project(str),lun(str)
pool_0,project1,lun01
pool_0,project1,lun02
pool_0,project1,lun03
pool_0,project1,lun04
```

**Note**: The csv files for lun creation and deletion are different, because we are trying to avoid a serious mistake using the same files, but listing can be done with any csv file.

Available values and types:

* pool: string
* project: string
* lun: string
* size: integer
* size_unit: "KB", "MB", "GB" or "TB" # Not case sensitive
* blocksize: "512", "1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k", "256k", "512k" or "1M" # Not case sensitive
* thin or sparse: True or False
* targetgroup: string
* initiatorgroup: string
* compression: "off", "lzjb", "gzip-2", "gzip" or "gzip-9"
* dedup: True or False
* nodestroy: True or False

Usage:

```text
$ ./zfssa-luns.py -h
usage: zfssa-luns.py [-h] -s SERVER -f FILE [-p] [-c | -d | -l]

Script to handle luns in ZFS Storage Appliance

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -f FILE, --file FILE  luns file (CSV)
  -p, --progress        progress bar and logging to file
  -c, --create          Create luns specified in csv file
  -d, --delete          Delete luns specified in csv file
  -l, --list            List/Check luns specified in csv file
```

Create luns.

```text
$./zfssa-luns.py -s server.yml -f luns_create.csv -c
###############################################################################
Creating luns from luns_create.csv
###############################################################################
CREATE - SUCCESS - lun 'lun01', project 'project1', pool 'pool_0'
===============================================================================
CREATE - SUCCESS - lun 'lun02', project 'project1', pool 'pool_0'
===============================================================================
CREATE - SUCCESS - lun 'lun03', project 'project1', pool 'pool_0'
===============================================================================
CREATE - FAIL - lun 'lun04', project 'project1', pool 'pool_0' - Error invalid input argument (bad property value "vmcluster" (expecting one of "default", "cluster-iscsi", "cluster-clone" or "cluster-test") (encountered while attempting to run command "set initiatorgroup="vmcluster""))
===============================================================================
Finished in 72 seconds
```

List luns:

```text
$ ./zfssa-luns.py -s server.yml -f luns_create.csv -l
###############################################################################
Listing luns
###############################################################################
LIST - PRESENT - name 'lun01' project 'project1' project 'pool_0' assigned number '3' initiatorgroup '[u'cluster-test']' volsize '1073741824.0' volblocksize '131072' status 'online' space_total '16384.0' lunguid '600144F0EF0D2BCE0000592A3D790007' logbias 'latency' creation '20170528T03:01:03' thin 'True' nodestroy 'False'
===============================================================================
LIST - PRESENT - name 'lun02' project 'project1' project 'pool_0' assigned number '4' initiatorgroup '[u'cluster-test']' volsize '2147483648.0' volblocksize '65536' status 'online' space_total '16384.0' lunguid '600144F0EF0D2BCE0000592A3D920008' logbias 'latency' creation '20170528T03:01:23' thin 'True' nodestroy 'True'
===============================================================================
LIST - PRESENT - name 'lun03' project 'project1' project 'pool_0' assigned number '5' initiatorgroup '[u'default']' volsize '1073741824.0' volblocksize '8192' status 'online' space_total '1107820544.0' lunguid '600144F0EF0D2BCE0000592A3DAC0009' logbias 'latency' creation '20170528T03:01:49' thin 'False' nodestroy 'False'
===============================================================================
LIST - FAIL - lun 'lun04', pool 'project1', project, 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun04
===============================================================================
Finished in 0 seconds
```

Delete luns:

```text
###############################################################################
Deleting luns from luns_destroy.csv
###############################################################################
DELETE - SUCCESS - lun 'lun01', pool 'pool_0', project 'project1'
===============================================================================
DELETE - FAIL - lun 'lun02', pool 'project1', project 'pool_0' - Error 403 Client Error: Forbidden for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun02
===============================================================================
DELETE - SUCCESS - lun 'lun03', pool 'pool_0', project 'project1'
===============================================================================
DELETE - FAIL - lun 'lun04', pool 'project1', project 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun04
===============================================================================
Finished in 35 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating snapshots with progress option:

```text
$./zfssa-luns.py -s server.yml -f luns_create.csv -c -p
Processing |################                | 2/4 - remain: 2 - 50.0% - 25s
```

Output file example.

```text
$ cat luns_output.log
2017-05-28 03:20:18,516 - luns - INFO - CREATE - SUCCESS - lun 'lun01', project 'project1', pool 'pool_0'
2017-05-28 03:20:20,376 - luns - WARNING - CREATE - FAIL - lun 'lun02', project 'project1', pool 'pool_0' - Error request creates an object that already exists (share "lun02" already exists (use "select lun02" to select it) (encountered while attempting to run command "lun lun02"))
2017-05-28 03:20:39,419 - luns - INFO - CREATE - SUCCESS - lun 'lun03', project 'project1', pool 'pool_0'
2017-05-28 03:20:41,421 - luns - WARNING - CREATE - FAIL - lun 'lun04', project 'project1', pool 'pool_0' - Error invalid input argument (bad property value "vmcluster" (expecting one of "default", "cluster-iscsi", "cluster-clone" or "cluster-test") (encountered while attempting to run command "set initiatorgroup="vmcluster""))
```
