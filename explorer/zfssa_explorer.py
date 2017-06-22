#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: Jun 20, 2017 3:51 PM
# @Author: Aldo Sotolongo
# @Contact: aldenso@gmail.com
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: Jun 20, 2017 7:01 PM
# @Description: Modify Here, Please

from __future__ import print_function, division
# import re
import os
# import json
import csv
from datetime import datetime
# import ast
import argparse
# import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
#from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import InsecureRequestWarning
import yaml

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.urllib3.disable_warnings(InsecureRequestWarning)

START = datetime.now()
OUTPUTDIR = "zfssa_explorer_{}".format(datetime.now().strftime("%d%m%y_%H%M%S"))
ZFSURL = ""  # API URL (https://example:215/api)
ZAUTH = ()   # API Authentication tuple (username, password)
HEADER = {"Content-Type": "application/json"}
LOGFILE = "explorer_output.log"


def create_parser():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Script to get ZFS Storage Appliance info")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)", required=True)
    # parser.add_argument(
    #     "-p", "--progress", action="store_true", help="progress bar and logging to file",
    #     required=False)
    return parser


def read_yaml_file(configfile):
    """Read config file and return credentials in json."""
    config = {}
    try:
        config = yaml.load(file(configfile, 'r'))
    except yaml.YAMLError as error:
        print("Error in configuration file: {}").format(error)
    return config


def response_size(size):
    if len(str(int(size))) <= 3:
        return "{:.2f}".format(size)
    elif len(str(int(size))) <= 6:
        return "{:.2f}KB".format(size / 1024)
    elif len(str(int(size))) <= 9:
        return "{:.2f}MB".format(size / (1024 * 1024))
    elif len(str(int(size))) <= 12:
        return "{:.2f}GB".format(size / (1024 * 1024 * 1024))
    elif len(str(int(size))) > 12:
        return "{:.2f}TB".format(size / (1024 * 1024 * 1024 * 1024))


def fetch(url, timeout, datatype):
    """Fetch data from zfs api"""
    req = requests.get(url, timeout=timeout, auth=ZAUTH, verify=False, headers=HEADER)
    data = req.json()
    return data, datatype

def printdata(data, datatype):
    """Print data in a human readable way"""
    if not os.path.exists(OUTPUTDIR):
        os.makedirs(OUTPUTDIR)
    if datatype == "version":
        print("#" * 100)
        print("ZFS Storage Appliance version")
        print("#" * 100)
        print("{:22} {:22} {:25} {:12} {:10}".format("nodename", "product", "version", "csn",
                                                     "sp_version"))
        print("{:22} {:22} {:25} {:12} {:10}".format(data['version']['nodename'],
                                                     data['version']['product'],
                                                     data['version']['version'],
                                                     data['version']['csn'],
                                                     data['version']['sp_version']))
        createCSV(data, datatype)
    elif datatype == "datalinks":
        print("#" * 100)
        print("datalink info")
        print("#" * 100)
        print("{:15} {:10} {:20} {:8} {:5} {:5}".format("datalink", "class", "label", "speed",
                                                        "id", "mtu"))
        for dlink in data['datalinks']:
            if dlink['class'] != "vlan":
                print("{:15} {:10} {:20} {:8} {:5} {:5}".format(dlink['datalink'], dlink['class'],
                                                                dlink['label'], dlink['speed'],
                                                                "", dlink['mtu']))
            else:
                print("{:15} {:10} {:20} {:8} {:5} {:5}".format(dlink['datalink'], dlink['class'],
                                                                dlink['label'], "", dlink['id'],
                                                                dlink['mtu']))
        createCSV(data, datatype)
    elif datatype == "devices":
        print("#" * 100)
        print("devices info")
        print("#" * 100)
        print("{:10} {:5} {:15} {:25} {:10} {:12} {:4}".format("device", "active", "duplex", "mac",
                                                               "media", "speed", "up"))
        for dev in data['devices']:
            print("{:10} {:5} {:15} {:25} {:10} {:12} {:4}".format(dev['device'], dev['active'],
                                                                   dev['duplex'],
                                                                   dev['factory_mac'],
                                                                   dev['media'], dev['speed'],
                                                                   dev['up']))
        createCSV(data, datatype)
    elif datatype == "interfaces":
        print("#" * 100)
        print("interfaces info")
        print("#" * 100)
        print("{:12} {:10} {:20} {:5} {:8} {:25} {:5}".format("interface", "class", "label",
                                                              "admin", "state", "v4addrs",
                                                              "enable"))
        for iface in data['interfaces']:
            print("{:12} {:10} {:20} {:5} {:8} {:25} {:5}".format(iface['interface'],
                                                                  iface['class'], iface['label'],
                                                                  iface['admin'], iface['state'],
                                                                  iface['v4addrs'],
                                                                  iface['enable']))
        createCSV(data, datatype)
    elif datatype == "projects":
        print("#" * 100)
        print("projects info")
        print("#" * 100)
        print("{:15} {:25} {:8} {:10} {:10} {:10}".format("name", "mountpoint", "pool", "quota",
                                                          "reserv", "space_total"))
        for proj in data['projects']:
            print("{:15} {:25} {:8} {:10} {:10} {:10}"\
                  .format(proj['name'], proj['mountpoint'], proj['pool'],
                          response_size(proj['quota']), response_size(proj['reservation']),
                          response_size(proj['space_total'])))
    elif datatype == "luns":
        print("#" * 100)
        print("luns info")
        print("#" * 100)
        print("{:10} {:15} {:8} {:10} {:10} {:12} {:8} {:25}".format("name", "project", "pool",
                                                                     "volsize", "vblocksize",
                                                                     "initiatorgroup", "status",
                                                                     "lunguid"))
        for lun in data['luns']:
            print("{:10} {:15} {:8} {:10} {:10} {:12} {:8} {:25}"\
                  .format(lun['name'], lun['project'], lun['pool'], response_size(lun['volsize']),
                          response_size(lun['volblocksize']), lun['initiatorgroup'], lun['status'],
                          lun['lunguid']))
    elif datatype == "filesystems":
        print("#" * 100)
        print("filesystems info")
        print("#" * 100)
        print("{:10} {:15} {:8} {:10} {:10} {:10} {:12}"\
              .format("name", "project", "pool", "quota", "reserv", "space_total", "mountpoint"))
        for fs in data['filesystems']:
            print("{:10} {:15} {:8} {:10} {:10} {:10} {:12}"\
                  .format(fs['name'], fs['project'], fs['pool'], response_size(fs['quota']),
                          response_size(fs['reservation']), response_size(fs['space_total']),
                          fs['mountpoint']))


def createCSV(data, datatype):
    if datatype == "version":
        d = data['version']
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['href', 'nodename', 'mkt_product', 'product', 'version',
                             'install_time', 'update_time', 'boot_time', 'asn', 'csn',
                             'part', 'urn', 'navname', 'navagent', 'http', 'ssl',
                             'ak_version', 'os_version', 'bios_version', 'sp_version'])
            writer.writerow([d['href'], d['nodename'], d['mkt_product'], d['product'],
                             d['version'], d['install_time'], d['update_time'],
                             d['boot_time'], d['asn'], d['csn'], d['part'], d['urn'],
                             d['navname'], d['navagent'], d['http'], d['ssl'],
                             d['ak_version'], d['os_version'], d['bios_version'],
                             d['sp_version']])
    if datatype == "datalinks":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['class', 'label', 'mac', 'links', 'mtu', 'id', 'speed', 'duplex',
                             'datalink', 'href'])
            for d in data['datalinks']:
                if d['class'] == "vlan":
                    writer.writerow([d['class'], d['label'], d['mac'], d['links'], d['mtu'],
                                     d['id'], "-", "-", d['datalink'], d['href']])
                else:
                    writer.writerow([d['class'], d['label'], d['mac'], d['links'], d['mtu'], "-",
                                     d['speed'], d['duplex'], d['datalink'], d['href']])
    if datatype == "devices":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['speed', 'up', 'active', 'media', 'factory_mac', 'port', 'guid',
                             'duplex', 'device', 'href'])
            for d in data['devices']:
                if d['media'] == "Infiniband":
                    writer.writerow([d['speed'], d['up'], d['active'], d['media'], d['factory_mac'],
                                     d['port'], d['guid'], "-", d['device'], d['href']])
                else:
                    writer.writerow([d['speed'], d['up'], d['active'], d['media'], d['factory_mac'],
                                     "-", "-", d['duplex'], d['device'], d['href']])
    if datatype == "interfaces":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['state', 'curaddrs', 'class', 'label', 'enable', 'admin', 'links',
                             'v4addrs', 'v4dhcp', 'v4directnets', 'v6addrs', 'v6dhcp',
                             'v6directnets', 'key', 'standbys', 'interface', 'href'])
            for d in data['interfaces']:
                if d['class'] == "ipmp":
                    writer.writerow([d['state'], d['curaddrs'], d['class'], d['label'],
                                     d['enable'], d['admin'], d['links'], d['v4addrs'],
                                     d['v4dhcp'], d['v4directnets'], d['v6addrs'], d['v6dhcp'],
                                     d['v6directnets'], d['key'], d['standbys'], d['interface'],
                                     d['href']])
                else:
                    writer.writerow([d['state'], d['curaddrs'], d['class'], d['label'],
                                     d['enable'], d['admin'], d['links'], d['v4addrs'],
                                     d['v4dhcp'], d['v4directnets'], d['v6addrs'], d['v6dhcp'],
                                     d['v6directnets'], "-", "-", d['interface'], d['href']])


def main(args):
    configfile = args.server
    config = read_yaml_file(configfile)
    global ZFSURL, ZAUTH
    ZFSURL = "https://{}:215/api".format(config['ip'])
    ZAUTH = (config['username'], config['password'])
    group1 = [("{}/system/v1/version".format(ZFSURL), "version"),
              #("{}/hardware/v1/cluster".format(ZFSURL), "cluster")
              ("{}/network/v1/datalinks".format(ZFSURL), "datalinks"),
              ("{}/network/v1/devices".format(ZFSURL), "devices"),
              ("{}/network/v1/interfaces".format(ZFSURL), "interfaces"),
              ("{}/storage/v1/projects".format(ZFSURL), "projects"),
              ("{}/storage/v1/luns".format(ZFSURL), "luns"),
              ("{}/storage/v1/filesystems".format(ZFSURL), "filesystems")]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for i in group1:
            url = i[0]
            future = executor.submit(fetch, url, 100, i[1])
            futures[future] = url

        for future in as_completed(futures):
            url = futures[future]
            try:
                data, datatype = future.result()
            except Exception as exc:
                print(exc)
            else:
                printdata(data, datatype)
        delta = datetime.now() - START
        print("Finished in {} seconds".format(delta.seconds))


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    # if args.progress:
    #     try:
    #         from progress.bar import Bar
    #     except ImportError as err:
    #         print("You need to install progress: pip install progress - Error: {}".format(err))
    #         exit(1)
    main(args)
