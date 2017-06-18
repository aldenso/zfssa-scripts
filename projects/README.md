# zfssa_projects.py

Script to create, delete and list projects in ZFS Storage Appliance (tested on OS8.6 and OS8.7).

config or server file must be yaml.

Example

```yml
ip: 192.168.56.150
username: root
password: password
```

Projects file must be csv, and columns (20) must be in the next order for project **creation** or **listing**:

```text
pool,project,mountpoint,quota,reservation,compression,dedup,logbias,nodestroy,recordsize,readonly,atime,default_sparse,default_user,default_group,default_permissions,default_volblocksize,default_volsize,sharenfs,sharesmb
```

Example:

```text
#pool(str),project(str),mountpoint(str),quota(str),reservation(str),compression(str),dedup(bool),logbias(str),nodestroy(bool),recordsize(str),readonly(bool),atime(bool),default_sparse(bool),default_user(str),default_group(str),default_permissions(str),default_volblocksize(str),default_volsize(str),sharenfs(str),sharesmb(str)
pool_0,proj01,/export/proj01,10g,10g,gzip,True,latency,False,128k,False,True,True,nobody,other,750,128k,1g,on,off
pool_0,proj02,/export/proj02,None,None,off,False,latency,False,128k,False,False,True,root,root,700,128k,1g,"sec=sys,rw,ro=example.com:@192.168.56.200/32,root=example.com:@192.168.56.100/32",on
```

**Note**: don't remove the header from the file.

For project **deletion** or **listing**, the file must be csv and columns (2) must be in the next order:

```text
pool,project
```

Example:

```text
#pool(str),project(str)
pool_0,proj01
pool_0,proj02
```

**Note**: The csv files for project creation and deletion are different, because we are trying to avoid a serious mistake using the same files, but listing can be done with any csv file.

Available values and types:

* pool: string
* project: string
* mountpoint: string
* quota: string
* reservation: string
* compression: "off", "lzjb", "gzip-2", "gzip" or "gzip-9"
* dedup: boolean
* logbias: "latency" or "throughput"
* nodestroy: boolean
* recordsize: "512", "1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k", "256k", "512k" or "1M"
* readonly: boolean
* atime: boolean
* default_sparse (thin): boolean
* default_user: string
* default_group: string
* default_permissions: string
* default_volblocksize: "512", "1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k", "256k", "512k" or "1M"
* default_volsize: interger with string, example: 1g, 512m
* sharenfs: "off", "on" , "ro", "rw", or complex like "sec=sys,rw,root=@192.168.56.100/32"
* sharenfs: "off", "rw", "ro"

Usage:

```text
$ ./zfssa_projects.py -h
usage: zfssa_projects.py [-h] -s SERVER -f FILE [-p] [-c | -d | -l]

Script to handle projects in ZFS Storage Appliance

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -f FILE, --file FILE  projects file (CSV)
  -p, --progress        progress bar and logging to file
  -c, --create          Create projects specified in csv file
  -d, --delete          Delete projects specified in csv file
  -l, --list            List/Check projects specified in csv file
```

Create projects.

```text
$./zfssa_projects.py -s server.yml -f create_project.csv -c
###############################################################################
Creating projects
###############################################################################
CREATE - SUCCESS - project 'proj01' pool 'pool_0'
===============================================================================
CREATE - SUCCESS - project 'proj02' pool 'pool_0'
===============================================================================
Finished in 24 seconds
```

List projects:

```text
$./zfssa_projects.py -s server.yml -f create_project.csv -l
###############################################################################
Listing projects
###############################################################################
LIST - PRESENT - project 'proj01' pool 'pool_0' mountpoint '/export/proj01' quota '10.00GB' reservation '10.00GB' compression 'gzip' dedup 'True' logbias 'latency' nodestroy 'False' recordsize '128.00KB' readonly 'False' atime 'True' def_sparse 'True' def_user 'nobody' def_group 'other' def_perms '750' def_volblocksize '128.00KB' def_volsize '1.00GB' sharenfs 'on' sharesmb 'off'
===============================================================================
LIST - PRESENT - project 'proj02' pool 'pool_0' mountpoint '/export/proj02' quota '0.00' reservation '0.00' compression 'off' dedup 'False' logbias 'latency' nodestroy 'False' recordsize '128.00KB' readonly 'False' atime 'False' def_sparse 'True' def_user 'root' def_group 'root' def_perms '700' def_volblocksize '128.00KB' def_volsize '1.00GB' sharenfs 'sec=sys,rw,ro=example.com:@192.168.56.200/32,root=example.com:@192.168.56.100/32' sharesmb 'on'
===============================================================================
Finished in 1 seconds
```

Delete projects:

```text
$./zfssa_projects.py -s server.yml -f destroy_project.csv -d
###############################################################################
Deleting projects
###############################################################################
DELETE - SUCCESS - project 'proj01' pool 'pool_0'
===============================================================================
DELETE - SUCCESS - project 'proj02' pool 'pool_0'
===============================================================================
Finished in 22 seconds
```

Also you can use -p (--progress option) to check the advance and all the output will be logged to a file.

Creating projects with progress option:

```text
$./zfssa_projects.py -s server.yml -f create_project.csv -c -p
Processing |################                | 1/2 - remain: 2 - 50.0% - 15s
```

Output file example.

```text
$ cat projects_output.log
2017-06-18 17:28:15,207 - projects - INFO - CREATE - SUCCESS - project 'proj01' pool 'pool_0'
2017-06-18 17:28:22,430 - projects - INFO - CREATE - SUCCESS - project 'proj02' pool 'pool_0'
```
