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

Luns file must be csv, and columns must be in the next order:

```text
pool,project,lun,size,size_unit,blocksize,thin,targetgroup,initiatorgroup,compression,dedup
```

Example:

```text
#pool(str),project(str),lun(str),size(int),size_unit(str),blocksize(str),thin(bool),targetgroup(str),initiatorgroup(str),compression(str),dedup(bool)
pool_0,project1,lun01,1,gb,128k,True,default,cluster-test,gzip,False,False
pool_0,project1,lun02,2,gb,64k,True,default,cluster-test,off,False,False
pool_0,project1,lun03,1024,MB,8k,False,default,default,off,False,False
pool_0,project1,lun04,256,MB,512k,False,default,vmcluster,off,False,False
```

**Note**: don't remove the header from the file.

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

Usage:

```text
./zfssa-luns.py -h
usage: zfssa-luns.py [-h] -s SERVER -f FILE [-c | -d | -l]

Script to handle luns in ZFS Storage Appliance

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -f FILE, --file FILE  luns file (CSV)
  -c, --create          Create luns specified in csv file
  -d, --delete          Delete luns specified in csv file
  -l, --list            List/Check luns specified in csv file
```

Create luns.

```text
$./zfssa-luns.py -s server.yml -f luns.csv -c
###############################################################################
Creating luns from .\luns.csv
###############################################################################
Creating lun: 'lun01'
pool: pool_0, project: project1,
+++ SUCCESS +++
===============================================================================
Creating lun: 'lun02'
pool: pool_0, project: project1,
+++ SUCCESS +++
===============================================================================
Creating lun: 'lun03'
pool: pool_0, project: project1,
+++ SUCCESS +++
===============================================================================
Creating lun: 'lun04'
pool: pool_0, project: project1,
message: invalid input argument (bad property value "vmcluster" (expecting one of "default", "cluster-iscsi", "cluster-clone" or "cluster-test") (encountered while attempting to run command "set initiatorgroup="vmcluster""))
Error: 400 Client Error: Bad Request for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns
--- FAILED ---
===============================================================================
Finished in 66 seconds
```

List luns:

```text
$./zfssa-luns.py -s server.yml -f luns.csv -l
###############################################################################
Listing luns
###############################################################################
name: lun01
pool:pool_0
project: project1
assigned number:    3
initiatorgroup: [u'cluster-test']
volsize:    1073741824.0
volblocksize: 131072
status: online
space_total:        16384.0
lunguid: 600144F0EF0D2BCE00005923946F0009
logbias: latency
creation: 20170523T01:46:10
thin:     1
===============================================================================
name: lun02
pool:pool_0
project: project1
assigned number:    4
initiatorgroup: [u'cluster-test']
volsize:    2147483648.0
volblocksize: 65536
status: online
space_total:        16384.0
lunguid: 600144F0EF0D2BCE000059239484000A
logbias: latency
creation: 20170523T01:46:32
thin:     1
===============================================================================
name: lun03
pool:pool_0
project: project1
assigned number:    5
initiatorgroup: [u'default']
volsize:    1073741824.0
volblocksize:  8192
status: online
space_total:   1107820544.0
lunguid: 600144F0EF0D2BCE00005923949B000B
logbias: latency
creation: 20170523T01:46:54
thin:     0
===============================================================================
Failed request to check lun: 'lun04'
lun 'lun04' in project 'project1' and pool 'pool_0' doesn't exists.
===============================================================================
Finished in 1 seconds
```

Delete luns:

```text
./zfssa-luns.py -s server.yml -f luns.csv -d
###############################################################################
Deleting luns from .\luns.csv
###############################################################################
Deleting lun: 'lun01'
pool: pool_0, project: project1
+++ SUCCESS +++
===============================================================================
Deleting lun: 'lun02'
pool: pool_0, project: project1
+++ SUCCESS +++
===============================================================================
Deleting lun: 'lun03'
pool: pool_0, project: project1
+++ SUCCESS +++
===============================================================================
Deleting lun: 'lun04'
pool: pool_0, project: project1
Error: 404 Client Error: Not Found for url: https://192.168.56.150:215/api/storage/v1/pools/pool_0/projects/project1/luns/lun04
--- FAILED ---
===============================================================================
Finished in 51 seconds
```