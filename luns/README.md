zfssa_luns.py
==============

Script to create, delete and list luns in ZFS Storage Appliance (tested on OS8.6 and OS8.7).

config or server file must be yaml.

Example

```yml
ip: 192.168.56.150
username: root
password: password
```

Luns file must be csv, and columns (12) must be in the next order for lun **creation** or **listing**:

```text
pool,project,lun,size,size_unit,blocksize,thin,targetgroup,initiatorgroup,compression,logbias,nodestroy
```

Example:

```text
#pool(str),project(str),lun(str),size(int),size_unit(str),blocksize(str),thin(bool),targetgrp(str),initiatorgrp(str),compression(str),logbias(str),nodestroy(bool)
pool_0,project1,lun01,1,gb,128k,True,default,cluster-test,gzip,latency,False
pool_0,project1,lun02,2,gb,64k,True,default,cluster-test,off,throughput,True
pool_0,project1,lun03,1024,MB,8k,False,default,default,off,latency,False
pool_0,project1,lun04,256,MB,512k,False,default,vmcluster,off,latency,False
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
* logbias: "latency" or "throughput"
* nodestroy: True or False

Usage:

```text
$ ./zfssa_luns.py -h
usage: zfssa_luns.py [-h] -s SERVER -f FILE [-p] [-c | -d | -l]

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
$./zfssa_luns.py -s server.yml -f luns_create.csv -c
###############################################################################
Creating luns
###############################################################################
CREATE - SUCCESS - lun 'lun01' project 'project1' pool 'pool_0'
===============================================================================
CREATE - SUCCESS - lun 'lun02' project 'project1' pool 'pool_0'
===============================================================================
CREATE - SUCCESS - lun 'lun03' project 'project1' pool 'pool_0'
===============================================================================
CREATE - FAIL - lun 'lun04' project 'project1' pool 'pool_0' - Error invalid input argument (bad property value "vmcluster" (expecting one of "default", "cluster-iscsi", "cluster-clone" or "cluster-test") (encountered while attempting to run command "set initiatorgroup="vmcluster""))
===============================================================================
Finished in 73 seconds
```

List luns:

```text
$ ./zfssa_luns.py -s server.yml -f luns_create.csv -l
###############################################################################
Listing luns
###############################################################################
LIST - PRESENT - name 'lun01' project 'project1' pool 'pool_0' assigned number '1' initiatorgroup '[u'cluster-test']' volsize '1.00GB' volblocksize '128.00KB' status 'online' space_total '16.00KB' lunguid '600144F0EF0D2BCE00005946B13E0002' logbias 'latency' creation '20170618T16:58:27' thin 'True' nodestroy 'False'
===============================================================================
LIST - PRESENT - name 'lun02' project 'project1' pool 'pool_0' assigned number '2' initiatorgroup '[u'cluster-test']' volsize '2.00GB' volblocksize '64.00KB' status 'online' space_total '16.00KB' lunguid '600144F0EF0D2BCE00005946B1520003' logbias 'throughput' creation '20170618T16:58:48' thin 'True' nodestroy 'True'
===============================================================================
LIST - PRESENT - name 'lun03' project 'project1' pool 'pool_0' assigned number '3' initiatorgroup '[u'default']' volsize '1.00GB' volblocksize '1.00MB' status 'online' space_total '1.00GB' lunguid '600144F0EF0D2BCE00005946B16A0004' logbias 'latency' creation '20170618T16:59:08' thin 'False' nodestroy 'False'
===============================================================================
LIST - FAIL - lun 'lun04' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun04
===============================================================================
Finished in 1 seconds
```

Delete luns:

```text
$ ./zfssa_luns.py -s server.yml -f luns_destroy.csv -d
###############################################################################
Deleting luns
###############################################################################
DELETE - SUCCESS - lun 'lun01' project 'project1' pool 'pool_0'
===============================================================================
DELETE - FAIL - lun 'lun02' project 'project1' pool 'pool_0' - Error 403 Client Error: Forbidden for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun02
===============================================================================
DELETE - SUCCESS - lun 'lun03' project 'project1' pool 'pool_0'
===============================================================================
DELETE - FAIL - lun 'lun04' project 'project1' pool 'pool_0' - Error 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun04
===============================================================================
Finished in 40 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating luns with progress option:

```text
$./zfssa_luns.py -s server.yml -f luns_create.csv -c -p
Processing |################                | 2/4 - remain: 2 - 50.0% - 25s
```

Output file example.

```text
$ cat luns_output.log
2017-06-18 17:05:09,806 - luns - INFO - CREATE - SUCCESS - lun 'lun01' project 'project1' pool 'pool_0'
2017-06-18 17:05:11,684 - luns - WARNING - CREATE - FAIL - lun 'lun02' project 'project1' pool 'pool_0' - Error request creates an object that already exists (share "lun02" already exists (use "select lun02" to select it) (encountered while attempting to run command "lun lun02"))
2017-06-18 17:05:35,128 - luns - INFO - CREATE - SUCCESS - lun 'lun03' project 'project1' pool 'pool_0'
2017-06-18 17:05:37,042 - luns - WARNING - CREATE - FAIL - lun 'lun04' project 'project1' pool 'pool_0' - Error invalid input argument (bad property value "vmcluster" (expecting one of "default", "cluster-iscsi", "cluster-clone" or "cluster-test") (encountered while attempting to run command "set initiatorgroup="vmcluster""))
```
