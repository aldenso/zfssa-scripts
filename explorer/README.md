# zfssa_explorer.py

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
usage: zfssa_explorer.py [-h] -s SERVER [-p]

Script to get ZFS Storage Appliance info

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server config file (YAML)
  -p, --progress        progress bar
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

## Using the explorer in a docker container

* Step 1:

Clone the repository to your docker host.

```sh
git clone https://github.com/aldenso/zfssa-scripts
```

* Step 2:

Change the directory to the repository and create a couple of directories to store the zfssa yaml configurations and the output zip files, also adjust what you want (ex: timezone in Dockerfile, scheduled times, etc).

```sh
cd zfssa-scripts
mkdir /tmp/datazfssa /tmp/zfssa_servers
cp yourzfssa01.yml yourzfssa02.yml ... /tmp/zfssa_servers # You can use server.yml as a template for your new files
```

Adjust timezone and times if you want:

```Dockerfile
RUN cp /usr/share/zoneinfo/America/Caracas /etc/localtime
RUN echo "America/Caracas" >  /etc/timezone
.
.
.
ENTRYPOINT ["python", "-u", "explorer_scheduler.py", "-d", "/zfssa-scripts/servers", "-t", "10:00", "-t", "22:00"]
```

* Step 3:

Build the image.

```sh
sudo docker build -t yourname/zfssaexplorer explorer
```

* Step 4:

Run a container using volumes according to what you defined.

```sh
sudo docker run -d -v /tmp/datazfssa:/zfssa-scripts/data \
-v /tmp/zfssa_servers:/zfssa-scripts/servers yourname/zfssaexplorer
```

or change the ENVs for your convenience.

```sh
sudo docker run -d -v /tmp/datazfssa:/zfssa-scripts/data \
-v /tmp/zfssa_servers:/zfssa-scripts/servers -e TIMES="09:00 16:00" yourname/zfssaexplorer
```

* Step 5:

Check your outputs:

```sh
ls -lrth /tmp/datazfssa
sudo docker logs <containerid>
```
