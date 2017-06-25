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


def exists(data, key):
    try:
        return data[key]
    except KeyError:
        return "-"

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
    elif datatype == "problems":
        print("#" * 100)
        print("problems info")
        print("#" * 100)
        for d in data['problems']:
            print("Type: {}\nSeverity: {}\nDescription: {}\nImpact: {}\nDiagnosed: {}"
                  .format(d['type'], d['severity'], d['description'], d['impact'], d['diagnosed']))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "datalinks":
        print("#" * 100)
        print("datalink info")
        print("#" * 100)
        print("{:15} {:10} {:20} {:8} {:5} {:5} {:5}".format("datalink", "class", "label", "speed",
                                                             "id", "mtu", "pkey"))
        for dlink in data['datalinks']:
            if dlink['class'] == "vlan":
                print("{:15} {:10} {:20} {:8} {:5} {:5} {:5}".format(dlink['datalink'],
                                                                     dlink['class'],
                                                                     dlink['label'], "",
                                                                     dlink['id'],
                                                                     dlink['mtu'], ""))
            elif dlink['class'] == "partition":
                print("{:15} {:10} {:20} {:8} {:5} {:5} {:5}".format(dlink['datalink'],
                                                                     dlink['class'],
                                                                     dlink['label'], "", "", "",
                                                                     dlink['pkey']))
            else:
                print("{:15} {:10} {:20} {:8} {:5} {:5} {:5}".format(dlink['datalink'],
                                                                     dlink['class'],
                                                                     dlink['label'], dlink['speed'],
                                                                     "", dlink['mtu'], ""))


        createCSV(data, datatype)
    elif datatype == "devices":
        print("#" * 100)
        print("devices info")
        print("#" * 100)
        print("{:10} {:5} {:15} {:25} {:10} {:12} {:4}".format("device", "active", "duplex", "mac",
                                                               "media", "speed", "up"))
        for dev in data['devices']:
            print("{:10} {:5} {:15} {:25} {:10} {:12} {:4}".format(dev['device'], dev['active'],
                                                                   exists(dev, 'duplex'),
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
    elif datatype == "routes":
        print("#" * 100)
        print("routes info")
        print("#" * 100)
        print("{:17} {:17} {:10} {:10} {:8} {:10}".format("gateway", "destination", "interface",
                                                          "type", "family", "status"))
        print("=" * 100)
        for d in data['routes']:
            print("{:17} {:17} {:10} {:10} {:8} {:10}".format(d['gateway'], d['destination'],
                                                              d['interface'], d['type'],
                                                              d['family'], d['status']))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "routing":
        print("#" * 100)
        print("routing info")
        print("#" * 100)
        print("{:15}".format("multihoming"))
        print("{:15}".format(data['routing']['multihoming']))
        createCSV(data, datatype)
    elif datatype == "pools":
        print("#" * 100)
        print("pools info")
        print("#" * 100)
        print("{:10} {:10} {:37} {:12} {:8} {:8} {:8} {:8} {:8}".format("name", "status", "profile",
                                                                        "owner", "total",
                                                                        "u_total", "used",
                                                                        "free", "avail"))
        for d in data['pools']:
            if d['status'] == "exported":
                print("{:10} {:10} {:37} {:12} {:8} {:8} {:8} {:8} {:8}"\
                      .format(d['name'], d['status'], "-", d['owner'],
                              "-", "-", "-", "-", "-"))
            else:
                u = d['usage']
                print("{:10} {:10} {:37} {:12} {:8} {:8} {:8} {:8} {:8}"\
                    .format(d['name'], d['status'], d['profile'], d['owner'],
                            response_size(u['total']), response_size(u['usage_total']),
                            response_size(u['used']), response_size(u['free']),
                            response_size(u['available'])))
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
        createCSV(data, datatype)
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
        createCSV(data, datatype)
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
        createCSV(data, datatype)
    elif datatype == "fc_initiators":
        print("#" * 100)
        print("fc initiators info")
        print("#" * 100)
        print("{:20} {:30}".format("alias", "initiator"))
        for d in data['initiators']:
            print("{:20} {:30}".format(d['alias'], d['initiator']))
        createCSV(data, datatype)
    elif datatype == "fc_initiator-groups":
        print("#" * 100)
        print("fc initiator-groups info")
        print("#" * 100)
        for d in data['groups']:
            print("name: {}\ninitiators: {}".format(d['name'], d['initiators']))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "fc_targets":
        print("#" * 100)
        print("fc targets info")
        print("#" * 100)
        for d in data['targets']:
            print("wwn: {}\nspeed: {}\nport: {}\ndiscoveredports: {}\nlink_failure_count: {}\t"\
                  "loss_of_sync_count: {}\tloss_of_signal_count: {}\nprotocol_error_count: {}\t"\
                  "invalid_tx_word_count: {}\tinvalid_crc_count: {}"\
                  .format(d['wwn'], d['speed'], d['port'], d['discovered_ports'],
                          d['link_failure_count'], d['loss_of_sync_count'],
                          d['loss_of_signal_count'], d['protocol_error_count'],
                          d['invalid_tx_word_count'], d['invalid_crc_count']))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "fc_target-groups":
        print("#" * 100)
        print("fc target-groups info")
        print("#" * 100)
        for d in data['groups']:
            print("name: {}\ntargets: {}".format(exists(d, 'name'), exists(d, 'targets')))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "iscsi_initiators":
        print("#" * 100)
        print("iscsi initiators info")
        print("#" * 100)
        for d in data['initiators']:
            print("alias: {}\ninitiator: {}\nchapuser: {}\nchapsecret: {}"\
                  .format(exists(d, 'alias'), exists(d, 'initiator'), exists(d, 'chapuser'),
                          exists(d, 'chapsecret')))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "iscsi_initiator-groups":
        print("#" * 100)
        print("iscsi initiator-groups info")
        print("#" * 100)
        for d in data['groups']:
            print("name: {}\ninitiators: {}".format(exists(d, 'name'), exists(d, 'initiators')))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "iscsi_targets":
        print("#" * 100)
        print("iscsi targets info")
        print("#" * 100)
        for d in data['targets']:
            print("alias: {}\niqn: {}\nauth: {}\ntargetchapuser: {}\ntargetchapsecret: {}\n"\
                  "interfaces: {}".format(exists(d, 'alias'), exists(d, 'iqn'), exists(d, 'auth'),
                                          exists(d, 'targetchapuser'),
                                          exists(d, 'targetchapsecret'), exists(d, 'interfaces')))
            print("=" * 100)
        createCSV(data, datatype)
    elif datatype == "iscsi_target-groups":
        print("#" * 100)
        print("iscsi target-groups info")
        print("#" * 100)
        for d in data['groups']:
            print("name: {}\ntargets: {}".format(d['name'], d['targets']))
            print("=" * 100)
        createCSV(data, datatype)


def createCSV(data, datatype):
    if datatype == "version":
        d = data['version']
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
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
    elif datatype == "problems":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["uuid", "code", "diagnosed", "phoned_home", "severity", "type", "url",
                             "description", "impact", "response", "action", "href"])
            for d in data['problems']:
                writer.writerow([d['uuid'], d['code'], d['diagnosed'], d['phoned_home'],
                                 d['severity'], d['type'], d['url'], d['description'], d['impact'],
                                 d['response'], d['action'], d['href']])
    elif datatype == "datalinks":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(['class', 'label', 'mac', 'links', 'pkey', 'linkmode', 'mtu', 'id',
                             'speed', 'duplex', 'datalink', 'href'])
            for d in data['datalinks']:
                writer.writerow([d['class'], d['label'], d['mac'], d['links'], exists(d, 'pkey'),
                                 exists(d, 'linkmode'), exists(d, 'mtu'), exists(d, 'id'),
                                 exists(d, 'speed'), exists(d, 'duplex'), d['datalink'], d['href']])
    elif datatype == "devices":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(['speed', 'up', 'active', 'media', 'factory_mac', 'port', 'guid',
                             'duplex', 'device', 'href'])
            for d in data['devices']:
                writer.writerow([d['speed'], d['up'], d['active'], d['media'], d['factory_mac'],
                                 exists(d, 'port'), exists(d, 'guid'), exists(d, 'duplex'),
                                 d['device'], d['href']])
    elif datatype == "interfaces":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(['state', 'curaddrs', 'class', 'label', 'enable', 'admin', 'links',
                             'v4addrs', 'v4dhcp', 'v4directnets', 'v6addrs', 'v6dhcp',
                             'v6directnets', 'key', 'standbys', 'interface', 'href'])
            for d in data['interfaces']:
                writer.writerow([d['state'], d['curaddrs'], d['class'], d['label'],
                                 d['enable'], d['admin'], d['links'], d['v4addrs'],
                                 d['v4dhcp'], d['v4directnets'], d['v6addrs'], d['v6dhcp'],
                                 d['v6directnets'], exists(d, 'key'), exists(d, 'standbys'),
                                 d['interface'], d['href']])
    elif datatype == "routes":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["status", "family", "destination", "mask", "href", "interface", "type",
                             "gateway"])
            for d in data['routes']:
                writer.writerow([d['status'], d['family'], d['destination'], d['mask'], d['href'],
                                 d['interface'], d['type'], d['gateway']])
    elif datatype == "routing":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["href", "multihoming"])
            writer.writerow([data['routing']['href'], data['routing']['multihoming']])
    elif datatype == "pools":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(['status', 'profile', 'name', 'usage_available',
                             'usage_usage_snapshots', 'usage_used', 'usage_compression',
                             'usage_usage_data', 'usage_free', 'usage_dedupratio', 'usage_total',
                             'usage_usage_total', 'peer', 'href', 'owner', 'asn'])
            for d in data['pools']:
                if d['status'] == "exported":
                    writer.writerow([d['status'], "-", d['name'], "-", "-", "-", "-", "-", "-",
                                     "-", "-", "-", d['peer'], d['href'], d['owner'], d['asn']])
                else:
                    u = d['usage']
                    writer.writerow([d['status'], d['profile'], d['name'],
                                     response_size(u['available']),
                                     response_size(u['usage_snapshots']), response_size(u['used']),
                                     u['compression'], response_size(u['usage_data']),
                                     response_size(u['free']), u['dedupratio'],
                                     response_size(u['total']), response_size(u['usage_total']),
                                     d['peer'], exists(d, 'href'), d['owner'], d['asn']])
    elif datatype == "projects":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(['snapdir', 'default_volblocksize', 'defaultgroupquota', 'logbias',
                             'creation', 'nodestroy', 'dedup', 'sharenfs', 'href', 'sharesmb',
                             'default_permissions', 'mountpoint', 'snaplabel', 'id', 'readonly',
                             'space_data', 'compression', 'defaultuserquota', 'src_snapdir',
                             'src_logbias', 'src_dedup', 'src_sharenfs', 'src_sharesmb',
                             'src_mountpoint', 'src_rrsrc_actions', 'src_compression',
                             'src_sharetftp', 'src_encryption', 'src_sharedav', 'src_copies',
                             'src_aclinherit', 'src_shareftp', 'src_readonly', 'src_keychangedate',
                             'src_secondarycache', 'src_maxblocksize', 'src_exported', 'src_vscan',
                             'src_reservation', 'src_atime', 'src_recordsize', 'src_checksum',
                             'src_sharesftp', 'src_nbmand', 'src_aclmode', 'src_rstchown',
                             'default_sparse', 'encryption', 'aclmode', 'copies', 'aclinherit',
                             'compressratio', 'shareftp', 'canonical_name', 'recordsize',
                             'keychangedate', 'space_available', 'secondarycache', 'name',
                             'space_snapshots', 'space_unused_res', 'quota', 'maxblocksize',
                             'exported', 'default_volsize', 'vscan', 'reservation', 'keystatus',
                             'atime', 'pool', 'default_user', 'space_unused_res_shares',
                             'sharetftp', 'checksum', 'space_total', 'default_group', 'sharesftp',
                             'rstchown', 'sharedav', 'nbmand'])
            for d in data['projects']:
                s = d['source']
                writer.writerow([d['snapdir'], response_size(d['default_volblocksize']),
                                 d['defaultgroupquota'], d['logbias'], d['creation'],
                                 d['nodestroy'], d['dedup'], d['sharenfs'], d['href'],
                                 d['sharesmb'], d['default_permissions'], d['mountpoint'],
                                 d['snaplabel'], d['id'], d['readonly'],
                                 response_size(d['space_data']), d['compression'],
                                 d['defaultuserquota'], s['snapdir'], s['logbias'], s['dedup'],
                                 s['sharenfs'], s['sharesmb'], s['mountpoint'],
                                 exists(s, 'rrsrc_actions'), s['compression'], s['sharetftp'],
                                 exists(s, 'encryption'), s['sharedav'], s['copies'],
                                 s['aclinherit'], s['shareftp'], s['readonly'], s['keychangedate'],
                                 s['secondarycache'], s['maxblocksize'], s['exported'], s['vscan'],
                                 s['reservation'], s['atime'], s['recordsize'], s['checksum'],
                                 s['sharesftp'], s['nbmand'], s['aclmode'], s['rstchown'],
                                 d['default_sparse'], d['encryption'], d['aclmode'], d['copies'],
                                 d['aclinherit'], d['compressratio'], d['shareftp'],
                                 d['canonical_name'], response_size(d['recordsize']),
                                 d['keychangedate'], response_size(d['space_available']),
                                 d['secondarycache'], d['name'],
                                 response_size(d['space_snapshots']),
                                 response_size(d['space_unused_res']), response_size(d['quota']),
                                 response_size(d['maxblocksize']), d['exported'],
                                 response_size(d['default_volsize']), d['vscan'],
                                 response_size(d['reservation']), d['keystatus'], d['atime'],
                                 d['pool'], d['default_user'],
                                 response_size(d['space_unused_res_shares']), d['sharetftp'],
                                 d['checksum'], response_size(d['space_total']),
                                 d['default_group'], d['sharesftp'], d['rstchown'], d['sharedav'],
                                 d['nbmand']])
    elif datatype == "luns":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["logbias", "creation", "nodestroy", "assignednumber", "copies",
                             "href", "fixednumber", "space_data", "id", "writecache",
                             "compression", "encryption", "dedup", "snaplabel", "compressratio",
                             "src_compression", "src_encryption", "src_logbias", "src_dedup",
                             "src_copies", "src_maxblocksize", "src_exported", "src_checksum",
                             "src_keychangedate", "src_rrsrc_actions", "src_secondarycache",
                             "space_total", "lunumber", "keychangedate", "space_available",
                             "secondary_cache", "status", "space_snapshots", "lunguid",
                             "maxblocksize", "exported", "initiatorgroup", "volsize", "keystatus",
                             "pool", "volblocksize", "writelimit", "name", "checksum",
                             "canonical_name", "project", "sparse", "targetgroup",
                             "effectivewritelimit"])
            for d in data['luns']:
                s = d['source']
                writer.writerow([d['logbias'], d['creation'], d['nodestroy'], d['assignednumber'],
                                 d['copies'], d['href'], d['fixednumber'],
                                 response_size(d['space_data']), d['id'], d['writecache'],
                                 d['compression'], d['encryption'], d['dedup'], d['snaplabel'],
                                 d['compressratio'], s['compression'], exists(s, 'encryption'),
                                 s['logbias'], s['dedup'], s['copies'], s['maxblocksize'],
                                 s['exported'], s['checksum'], s['keychangedate'],
                                 exists(s, 'rrsrc_actions'), s['secondarycache'],
                                 response_size(d['space_total']), d['lunumber'],
                                 d['keychangedate'], response_size(d['space_available']),
                                 d['secondarycache'], d['status'],
                                 response_size(d['space_snapshots']), d['lunguid'],
                                 response_size(d['maxblocksize']), d['exported'],
                                 d['initiatorgroup'], response_size(d['volsize']), d['keystatus'],
                                 d['pool'], response_size(d['volblocksize']),
                                 exists(d, 'writelimit'), d['name'], d['checksum'],
                                 d['canonical_name'], d['project'], d['sparse'],
                                 d['targetgroup'], exists(d, 'effectivewritelimit')])
    elif datatype == "filesystems":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["snapdir", "logbias", "creation", "nodestroy", "dedup", "sharenfs",
                             "sharesmb_abe", "sharesmb", "root_acl", "mountpoint",
                             "casesensitivity", "snaplabel", "id", "readonly", "sharesmb_name",
                             "space_data", "compression", "sharetftp", "src_snapdir", "src_logbias",
                             "src_dedup", "src_sharenfs", "src_sharesmb", "src_mountpoint",
                             "src_rrsrc_actions", "src_compression", "src_sharetftp",
                             "src_encryption", "src_sharedav", "src_copies", "src_aclinherit",
                             "src_shareftp", "src_readonly", "src_keychangedate",
                             "src_secondarycache", "src_maxblocksize", "src_exported", "src_vscan",
                             "src_reservation", "src_atime", "src_recordsize", "src_checksum",
                             "src_sharesftp", "src_nbmand", "src_aclmode", "src_rstchown",
                             "encryption", "aclmode", "copies", "smbshareacl",
                             "aclinherit", "compressratio", "shareftp", "canonical_name",
                             "recordsize", "keychangedate", "space_available", "root_group",
                             "secondarycache", "root_user", "root_permissions", "shadow",
                             "space_snapshots", "href", "space_unused_res", "quota", "utf8only",
                             "sharesmb_dfsroot", "maxblocksize", "exported", "vscan", "reservation",
                             "keystatus", "atime", "pool", "quota_snap", "space_unused_res_shares",
                             "name", "checksum", "space_total", "project", "normalization",
                             "sharesftp", "rstchown", "reservation_snap", "sharedav", "nbmand"])
            for d in data['filesystems']:
                s = d['source']
                writer.writerow([d['snapdir'], d['logbias'], d['creation'], d['nodestroy'],
                                 d['dedup'], d['sharenfs'], exists(d, 'sharesmb_abe'),
                                 d['sharesmb'], exists(d, 'root_acl'), d['mountpoint'],
                                 d['casesensitivity'], d['snaplabel'], d['id'], d['readonly'],
                                 exists(d, 'sharesmb_name'), response_size(d['space_data']),
                                 d['compression'], d['sharetftp'], s['snapdir'], s['logbias'],
                                 s['dedup'], s['sharenfs'], s['sharesmb'], s['mountpoint'],
                                 exists(s, 'rrsrc_actions'), s['compression'], s['sharetftp'],
                                 exists(s, 'encryption'), s['sharedav'], s['copies'],
                                 s['aclinherit'], s['shareftp'], s['readonly'],
                                 s['keychangedate'], s['secondarycache'], s['maxblocksize'],
                                 s['exported'], s['vscan'], s['reservation'], s['atime'],
                                 s['recordsize'], s['checksum'], s['sharesftp'], s['nbmand'],
                                 s['aclmode'], s['rstchown'], d['encryption'], d['aclmode'],
                                 d['copies'], exists(d, 'smbshareacl'), d['aclinherit'],
                                 d['compressratio'], d['shareftp'], d['canonical_name'],
                                 response_size(d['recordsize']), d['keychangedate'],
                                 response_size(d['space_available']), d['root_group'],
                                 d['secondarycache'], d['root_user'], d['root_permissions'],
                                 d['shadow'], response_size(d['space_snapshots']), d['href'],
                                 response_size(d['space_unused_res']), response_size(d['quota']),
                                 d['utf8only'], exists(d, 'sharesmb_dfsroot'),
                                 response_size(d['maxblocksize']), d['exported'], d['vscan'],
                                 response_size(d['reservation']), d['keystatus'], d['atime'],
                                 d['pool'], response_size(d['quota_snap']),
                                 exists(d, 'space_unused_res_shares'), d['name'],
                                 d['checksum'], response_size(d['space_total']), d['project'],
                                 d['normalization'], d['sharesftp'], d['rstchown'],
                                 response_size(d['reservation_snap']), d['sharedav'], d['nbmand']])
    elif datatype == "fc_initiators":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["alias", "initiator", "href"])
            for d in data['initiators']:
                writer.writerow([d['alias'], d['initiator'], d['href']])
    elif datatype == "fc_initiator-groups":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["name", "initiators", "href"])
            for d in data['groups']:
                writer.writerow([d['name'], d['initiators'], d['href']])
    elif datatype == "fc_targets":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["wwn", "port", "mode", "speed", "discovered_ports",
                             "link_failure_count", "loss_of_sync_count", "loss_of_signal_count",
                             "protocol_error_count", "invalid_tx_word_count", "invalid_crc_count",
                             "href"])
            for d in data['targets']:
                writer.writerow([d['wwn'], d['port'], d['mode'], d['speed'],
                                 d['discovered_ports'], d['link_failure_count'],
                                 d['loss_of_sync_count'], d['loss_of_signal_count'],
                                 d['protocol_error_count'], d['invalid_tx_word_count'],
                                 d['invalid_crc_count'], d['href']])
    elif datatype == "fc_target-groups":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["name", "targets", "href"])
            for d in data['groups']:
                writer.writerow([exists(d, 'name'), exists(d, 'targets'), exists(d, 'href')])
    elif datatype == "iscsi_initiators":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["alias", "initiator", "chapuser", "chapsecret", "href"])
            for d in data['initiators']:
                writer.writerow([exists(d, 'alias'), exists(d, 'initiator'), exists(d, 'chapuser'),
                                 exists(d, 'chapsecret'), exists(d, 'href')])
    elif datatype == "iscsi_initiator-groups":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["name", "initiators", "href"])
            for d in data['groups']:
                writer.writerow([exists(d, 'name'), exists(d, 'initiators'), exists(d, 'href')])
    elif datatype == "iscsi_targets":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["alias", "iqn", "auth", "targetchapuser", "targetchapsecret",
                             "interfaces", "href"])
            for d in data['targets']:
                writer.writerow([exists(d, 'alias'), exists(d, 'iqn'), exists(d, 'auth'),
                                 exists(d, 'targetchapuser'), exists(d, 'targetchapsecret'),
                                 exists(d, 'interfaces'), exists(d, 'href')])
    elif datatype == "iscsi_target-groups":
        with open(os.path.join(OUTPUTDIR, '{}.csv'.format(datatype)), 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["sep=;"])
            writer.writerow(["name", "targets", "href"])
            for d in data['groups']:
                writer.writerow([exists(d, 'name'), exists(d, 'targets'), exists(d, 'href')])

def main(args):
    configfile = args.server
    config = read_yaml_file(configfile)
    global ZFSURL, ZAUTH
    ZFSURL = "https://{}:215/api".format(config['ip'])
    ZAUTH = (config['username'], config['password'])
    group1 = [("{}/system/v1/version".format(ZFSURL), "version"),
              #("{}/hardware/v1/cluster".format(ZFSURL), "cluster")
              ("{}/problem/v1/problems".format(ZFSURL), "problems"),
              ("{}/network/v1/datalinks".format(ZFSURL), "datalinks"),
              ("{}/network/v1/devices".format(ZFSURL), "devices"),
              ("{}/network/v1/interfaces".format(ZFSURL), "interfaces"),
              ("{}/network/v1/routes".format(ZFSURL), "routes"),
              ("{}/network/v1/routing".format(ZFSURL), "routing"),
              ("{}/storage/v1/pools".format(ZFSURL), "pools"),
              ("{}/storage/v1/projects".format(ZFSURL), "projects"),
              ("{}/storage/v1/luns".format(ZFSURL), "luns"),
              ("{}/storage/v1/filesystems".format(ZFSURL), "filesystems"),
              ("{}/san/v1/fc/initiators".format(ZFSURL), "fc_initiators"),
              ("{}/san/v1/fc/initiator-groups".format(ZFSURL), "fc_initiator-groups"),
              ("{}/san/v1/fc/targets".format(ZFSURL), "fc_targets"),
              ("{}/san/v1/fc/target-groups".format(ZFSURL), "fc_target-groups"),
              ("{}/san/v1/iscsi/initiators".format(ZFSURL), "iscsi_initiators"),
              ("{}/san/v1/iscsi/initiator-groups".format(ZFSURL), "iscsi_initiator-groups"),
              ("{}/san/v1/iscsi/targets".format(ZFSURL), "iscsi_targets"),
              ("{}/san/v1/iscsi/target-groups".format(ZFSURL), "iscsi_target-groups")]
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
