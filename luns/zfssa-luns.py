#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: May 21, 2017 9:01 PM 
# @Author: Aldo Sotolongo 
# @Contact: aldenso@gmail.com 
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: May 23, 2017 8:34 AM 
# @Description: Create, Delete and list luns defined in csv file.


from __future__ import print_function
import re
import json
import csv
from datetime import datetime
import ast
import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import HTTPError, ConnectionError
import yaml

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
        description="Script to handle luns in ZFS Storage Appliance")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)",
        required=True)
    parser.add_argument(
        "-f", "--file", type=str, help="luns file (CSV)", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create", action="store_true",
                       help="Create luns specified in csv file")
    group.add_argument("-d", "--delete", action="store_true",
                       help="Delete luns specified in csv file")
    group.add_argument("-l", "--list", action="store_true",
                       help="List/Check luns specified in csv file")
    args = parser.parse_args()
    return args


def read_lun_file(filename):
    """Read lun csv file and return the list."""
    lunlist = []
    with open(filename, 'rb') as cvsfile:
        filereader = csv.reader(cvsfile, delimiter=',')
        for row in filereader:
            lunlist.append(row)
    del lunlist[0]
    return lunlist


def read_yaml_file(configfile):
    """Read config file and return credentials in json."""
    config = {}
    try:
        config = yaml.load(file(configfile, 'r'))
    except yaml.YAMLError as error:
        print("Error in configuration file: {}").format(error)
    return config


def get_real_size(size, size_unit):
    """Get size in bytes for different unit sizes."""
    real_size = 0
    multiplier = {
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024
    }
    real_size = int(size) * (multiplier[size_unit.upper()])
    return real_size


def get_real_blocksize(blocksize):
    """Get integer blocksize from string"""
    if "k" or "K" in blocksize:
        string = re.sub(r"\d+", "", blocksize)
        blocksize = int(blocksize.replace(string, "")) * 1024
        return blocksize
    if "m" or "M" in blocksize:
        blocksize = int(blocksize.replace(string, "")) * 1024 * 1024
        return blocksize
    else:
        return blocksize

def create_lun(fileline):
    """Create LUN from csv file."""
    if len(fileline) != 11:
        print("Error in line: {} -  It needs to be 3 or 11 columns long".format(fileline))
        return
    pool, project, lun, size, size_unit, blocksize, thin, targetgroup, initiatorgroup,\
    compression, dedup = fileline
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/luns"\
                    .format(pool, project)
    converted_size = get_real_size(size, size_unit)
    real_blocksize = get_real_blocksize(blocksize)
    try:
        data = {"name": lun,
                "volsize": converted_size,
                "volblocksize": real_blocksize,
                "sparse": ast.literal_eval(thin),
                "targetgroup": targetgroup,
                "initiatorgroup": initiatorgroup,
                "compression": compression,
                "dedup": ast.literal_eval(dedup)}
        req = requests.post(fullurl, data=json.dumps(data),
                            auth=ZAUTH, verify=False, headers=HEADER)
        print("Creating lun: '{}'\npool: {}, project: {},"
              .format(lun, pool, project))
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
        if error.response.status_code == 401:
            print("Please check your user/password!")
            exit(1)
    except ConnectionError as error:
        print("Connection Error: {}".format(error.message))


def delete_lun(fileline):
    """Delete lun specified in csv file"""
    pool = project = lun = None
    if len(fileline) == 3:
        pool, project, lun = fileline
    if len(fileline) == 11:
        pool, project, lun, _, _, _, _, _, _, _, _ = fileline
    else:
        print("Error in line: {} -  It needs to be 3 or 11 columns long".format(fileline))
        return
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/luns/{}".format(pool, project, lun)
    if not None in [pool, project, lun]:
        try:
            req = requests.delete(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
            print("Deleting lun: '{}'\npool: {}, project: {}".format(lun, pool, project))
            req.close()
            req.raise_for_status()
            print("+++ SUCCESS +++")
        except HTTPError as error:
            print("Error: {}".format(error.message))
            print("--- FAILED ---")
            if error.response.status_code == 401:
                print("Please check your user/password!")
                exit(1)
        except ConnectionError as error:
            print("Connection Error: {}".format(error.message))


def list_lun(fileline):
    """List/Show lun specified in csv file"""
    pool = project = lun = None
    if len(fileline) == 3:
        pool, project, lun = fileline
    if len(fileline) == 11:
        pool, project, lun, _, _, _, _, _, _, _, _ = fileline
    else:
        print("Error in line: {} -  It needs to be 3 or 11 columns long".format(fileline))
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/luns/{}".format(pool, project, lun)
    if not None in [pool, project, lun]:
        try:
            req = requests.get(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
            j = json.loads(req.text)
            req.close()
            req.raise_for_status()
            print("name: {:15}\npool:{:8}\nproject: {:12}\nassigned number: {:4}\n"
                  "initiatorgroup: {:18}\nvolsize: {:15}\nvolblocksize: {:5}\n"
                  "status: {:10}\nspace_total:{:15}\nlunguid: {:40}\nlogbias: {:10}\n"
                  "creation: {:20}\nthin: {:5}"
                  .format(j["lun"]["name"],
                          j["lun"]["pool"],
                          j["lun"]["project"],
                          j["lun"]["assignednumber"],
                          j["lun"]["initiatorgroup"],
                          j["lun"]["volsize"],
                          j["lun"]["volblocksize"],
                          j["lun"]["status"],
                          j["lun"]["space_total"],
                          j["lun"]["lunguid"],
                          j["lun"]["logbias"],
                          j["lun"]["creation"],
                          j["lun"]["sparse"]))
        except HTTPError as error:
            print("Failed request to check lun: '{}'".format(lun))
            if error.response.status_code == 404:
                print("lun '{}' in project '{}' and pool '{}' doesn't exists."
                      .format(lun, project, pool))
            if error.response.status_code == 401:
                print("Error '{}'.".format(error.message))
                print("Please check your user/password!")
                exit(1)
        except ConnectionError as error:
            print("Connection Error: {}".format(error.message))


def run_luns():
    """Run all luns actions"""
    args = get_args()
    csvfile = args.file
    listlun = args.list
    createlun = args.create
    deletelun = args.delete
    lunlistfromfile = read_lun_file(csvfile)
    configfile = args.server
    config = read_yaml_file(configfile)
    global ZFSURL, ZAUTH
    ZFSURL = "https://{}:215/api".format(config['ip'])
    ZAUTH = (config['username'], config['password'])
    if createlun:
        print("#" * 79)
        print("Creating luns from {}".format(csvfile))
        print("#" * 79)
        for entry in lunlistfromfile:
            create_lun(entry)
            print("=" * 79)
    elif deletelun:
        print("#" * 79)
        print("Deleting luns from {}".format(csvfile))
        print("#" * 79)
        for entry in lunlistfromfile:
            delete_lun(entry)
            print("=" * 79)
    elif listlun:
        print("#" * 79)
        print("Listing luns")
        print("#" * 79)
        for entry in lunlistfromfile:
            list_lun(entry)
            print("=" * 79)
    else:
        print("#" * 79)
        print("You need to specify an option (--list, --create, --delete)")
        print("#" * 79)
    delta = datetime.now() - START
    print("Finished in {} seconds".format(delta.seconds))


if __name__ == "__main__":
    run_luns()
