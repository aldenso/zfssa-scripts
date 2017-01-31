#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: Aldo Sotolongo
# @Date:   2017-01-30 23:26:42
# @Last Modified by:   Aldo Sotolongo
# @Last Modified time: 2017-01-31 00:04:46
# Description: Create, Delete and list snapshots defined in csv file.


from __future__ import print_function
import json
import csv
from datetime import datetime
import argparse
import requests
import yaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import HTTPError, ConnectionError

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

START = datetime.now()
ZFSURL = ""  # API URL (https://example:215/api)
ZAUTH = ()   # API Authentication tuple (username, password)
HEADER = {"Content-Type": "application/json"}


def get_args():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Script to handle snapshots in ZFS Storage Appliance")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)",
        required=True)
    parser.add_argument(
        "-f", "--file", type=str, help="Snapshots file (CSV)", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create", action="store_true",
                       help="Create Snapshots specified in csv file")
    group.add_argument("-d", "--delete", action="store_true",
                       help="Delete Snapshots specified in csv file")
    group.add_argument("-l", "--list", action="store_true",
                       help="List/Check Snapshots specified in csv file")
    args = parser.parse_args()
    return args


def read_snap_file(filename):
    """Read snap csv file and return the list"""
    snaplist = []
    with open(filename, 'rb') as cvsfile:
        filereader = csv.reader(cvsfile, delimiter=',')
        for row in filereader:
            snaplist.append(row)
    return snaplist


def read_yaml_file(configfile):
    config = {}
    try:
        config = yaml.load(file(configfile, 'r'))
    except yaml.YAMLError as error:
        print("Error in configuration file: {}").format(error)
    return config


def create_snap(snap):
    """Create Snapshots from csv file"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots".format(pool, project, filesystem)
    try:
        req = requests.post(fullurl, data=json.dumps({'name': snapname}),
                            auth=ZAUTH, verify=False, headers=HEADER)
        print("Creating Snapshot: '{}'\npool: {}, project: {},"
              " filesystem: {}".format(snapname, pool,
                                       project, filesystem))
        j = json.loads(req.text)
        if 'fault' in j:
            if 'message' in j['fault']:
                print("message: {}".format(j['fault']['message']))
        req.close()
        req.raise_for_status()
        print("+++ SUCCESS +++")
    except HTTPError as error:
        print("Error: {}".format(error.message))
        print("--- FAILED ---")
    except ConnectionError as error:
        print("Connection Error: {}".format(error.message))


def delete_snap(snap):
    """Delete Snapshots specified in csv file"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots/{}".format(pool, project, filesystem,
                                             snapname)
    try:
        req = requests.delete(fullurl, auth=ZAUTH, verify=False,
                              headers=HEADER)
        print("Deleting Snapshot: '{}'\npool: {}, project: {},"
              " filesystem: {}".format(snapname, pool,
                                       project, filesystem))
        req.close()
        req.raise_for_status()
        print("+++ SUCCESS +++")
    except HTTPError as error:
        print("Error: {}".format(error.message))
        print("--- FAILED ---")
    except ConnectionError as error:
        print("Connection Error: {}".format(error.message))


def list_snap(snap):
    """List Snapshots specified in csv file"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots".format(pool, project, filesystem)
    try:
        req = requests.get(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        req.close()
        req.raise_for_status()
        if len(j['snapshots']) == 0:
            print("Snapshot: {} in pool: {}, project: {} and filesystem: {}"
                  " doesn't exists".format(snapname, pool,
                                           project, filesystem))
        else:
            for i in j['snapshots']:
                if i['name'] == snapname:
                    print("Snapshot: {}, created at: {}\n"
                          "pool: {}, project: {},"
                          " filesystem: {}\nspace data: {:.2f}GB space unique:"
                          " {:.2f}GB"
                          .format(i['name'], i['creation'], pool, project,
                                  filesystem, i['space_data'] / 1073741824,
                                  i['space_unique'] / 1073741824))
    except HTTPError as error:
        print("Failed request to check snapshot: '{}'".format(snapname))
        if error.response.status_code == 404:
            print("share '{}' in project '{}' and pool '{}' doesn't exists."
                  .format(filesystem, project, pool))
    except ConnectionError as error:
        print("Connection Error: {}".format(error.message))


def run_snaps():
    """Run all snapshots actions"""
    args = get_args()
    FILE = args.file
    listsnaps = args.list
    createsnaps = args.create
    deletesnaps = args.delete
    snaplist = read_snap_file(FILE)
    configfile = args.server
    config = read_yaml_file(configfile)
    global ZFSURL, ZAUTH
    ZFSURL = "https://{}:215/api".format(config['ip'])
    ZAUTH = (config['username'], config['password'])
    if createsnaps:
        print("#" * 79)
        print("Creating snapshots from {}".format(FILE))
        print("#" * 79)
        for entry in snaplist:
            create_snap(entry)
            print("=" * 79)
    elif deletesnaps:
        print("#" * 79)
        print("Deleting snapshots from {}".format(FILE))
        print("#" * 79)
        for entry in snaplist:
            delete_snap(entry)
            print("=" * 79)
    elif listsnaps:
        print("#" * 79)
        print("Listing snapshots")
        print("#" * 79)
        for entry in snaplist:
            list_snap(entry)
            print("=" * 79)
    delta = datetime.now() - START
    print("Finished in {} seconds".format(delta.seconds))


if __name__ == "__main__":
    run_snaps()
