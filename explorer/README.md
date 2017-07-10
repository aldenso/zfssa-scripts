zfssa_explorer.py
==============

Script to get ZFS Storage Appliance info (tested on OS8.6 and OS8.7).

config or server file must be yaml.

Example

```yml
ip: 192.168.56.150
username: root
password: password
```

Usage:

```text
$ ./zfssa_explorer.py -h
usage: zfssa_explorer.py [-h] -s SERVER

Script to get ZFS Storage Appliance info

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
```

Run explorer.

```text
$./zfssa_explorer.py -s server.yml
####################################################################################################
problems info
####################################################################################################
####################################################################################################
ZFS Storage Appliance version
####################################################################################################
nodename               product                version                   csn          sp_version
zfsnode1            Sun ZFS Storage 7420   2013.06.05.7.4,1-1.1      1XXXXXXXXX   3.2.7.20.a r112614
####################################################################################################
datalink info
####################################################################################################
datalink        class      label                speed    id    mtu   pkey
.
.
.
####################################################################################################
interfaces info
####################################################################################################
interface    class      label                admin state    v4addrs                   enable
igb0         ip         igb0_interface           1 up       [u'192.168.56.150/24']           1
ipmp1        ipmp       ipmp0                    0 up       [u'192.168.56.110/24']           1
Finished in 74 seconds
```

Results in csv format are generated in a zip file.

```text
zfssa_explorer_192.168.56.150_100717_152438.zip
```