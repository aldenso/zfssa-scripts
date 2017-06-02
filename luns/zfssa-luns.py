#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: May 21, 2017 9:01 PM 
# @Author: Aldo Sotolongo
# @Contact: aldenso@gmail.com
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: May 28, 2017 2:44 AM
# @Description: Create, Delete and list luns defined in csv file.


from __future__ import print_function
import re
import json
import csv
from datetime import datetime
import ast
import argparse
import logging
import requests
from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import InsecureRequestWarning
import yaml

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.urllib3.disable_warnings(InsecureRequestWarning)

START = datetime.now()
ZFSURL = ""  # API URL (https://example:215/api)
ZAUTH = ()   # API Authentication tuple (username, password)
HEADER = {"Content-Type": "application/json"}
LOGFILE = "luns_output.log"


def get_args():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Script to handle luns in ZFS Storage Appliance")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)",
        required=True)
    parser.add_argument(
        "-f", "--file", type=str, help="luns file (CSV)", required=True)
    parser.add_argument(
        "-p", "--progress", action="store_true", help="progress bar and logging to file",
        required=False)
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
    if ("k" or "K") in blocksize:
        string = re.sub(r"\d+", "", blocksize)
        blocksize = int(blocksize.replace(string, "")) * 1024
        return blocksize
    elif ("m" or "M") in blocksize:
        string = re.sub(r"\d+", "", blocksize)
        blocksize = int(blocksize.replace(string, "")) * 1024 * 1024
        return blocksize
    else:
        return blocksize

def create_lun(fileline):
    """Create LUN from csv file. (err, msg)"""
    if len(fileline) != 12:
        return True, "DELETE - FAIL - Error in line {} It needs to be 12 columns long"\
                     .format(fileline)
    pool, project, lun, size, size_unit, blocksize, thin, targetgroup, initiatorgroup,\
    compression, latency, nodestroy = fileline
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
                "logbias": latency,
                "nodestroy": ast.literal_eval(nodestroy)}
        req = requests.post(fullurl, data=json.dumps(data),
                            auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        if 'fault' in j:
            if 'message' in j['fault']:
                return True, "CREATE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                             .format(lun, project, pool, j['fault']['message'])
        req.close()
        req.raise_for_status()
        return False, "CREATE - SUCCESS - lun '{}', project '{}', pool '{}'".format(lun, project,
                                                                                    pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("CREATE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                 .format(lun, project, pool, error.message))
        else:
            return True, "CREATE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                         .format(lun, project, pool, error.message)
    except ConnectionError as error:
        return True, "CREATE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                     .format(lun, project, pool, error.message)


def delete_lun(fileline):
    """Delete lun specified in csv file (err, msg)"""
    if len(fileline) != 3:
        return True, "DELETE - FAIL - Error in line {} It needs to be 3 columns long"\
                     .format(fileline)
    pool, project, lun = fileline
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/luns/{}".format(pool, project, lun)
    try:
        req = requests.delete(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        req.close()
        req.raise_for_status()
        return False, "DELETE - SUCCESS - lun '{}', project '{}', pool '{}'".format(lun, project,
                                                                                    pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("DELETE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                 .format(lun, project, pool, error.message))
        else:
            return True, "DELETE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                         .format(lun, project, pool, error.message)
    except ConnectionError as error:
        return True, "DELETE - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                     .format(lun, project, pool, error.message)


def list_lun(fileline):
    """List/Show lun specified in csv file (err, msg)"""
    pool = project = lun = None
    if len(fileline) == 3:
        pool, project, lun = fileline
    elif len(fileline) == 12:
        pool, project, lun, _, _, _, _, _, _, _, _, _ = fileline
    else:
        return True, "LIST - FAIL - Error in line {} It needs to be 3 or 12 columns long"\
                     .format(fileline)
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/luns/{}".format(pool, project, lun)
    try:
        req = requests.get(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        req.close()
        req.raise_for_status()
        return False, "LIST - PRESENT - name '{}' project '{}' pool '{}' assigned number '{}' "\
                      "initiatorgroup '{}' volsize '{}' volblocksize '{}' status '{}' "\
                      "space_total '{}' lunguid '{}' logbias '{}' creation '{}' thin '{}' "\
                      "nodestroy '{}'".format(j["lun"]["name"],
                                              j["lun"]["project"],
                                              j["lun"]["pool"],
                                              j["lun"]["assignednumber"],
                                              j["lun"]["initiatorgroup"],
                                              j["lun"]["volsize"],
                                              j["lun"]["volblocksize"],
                                              j["lun"]["status"],
                                              j["lun"]["space_total"],
                                              j["lun"]["lunguid"],
                                              j["lun"]["logbias"],
                                              j["lun"]["creation"],
                                              j["lun"]["sparse"],
                                              j["lun"]["nodestroy"])
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("LIST - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                 .format(lun, project, pool, error.message))
        else:
            return True, "LIST - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                         .format(lun, project, pool, error.message)
    except ConnectionError as error:
        return True, "LIST - FAIL - lun '{}', project '{}', pool '{}' - Error {}"\
                        .format(lun, project, pool, error.message)


def createprogress(count):
    """Return Bar class with max size specified"""
    progressbar = Bar(message='Processing',
                      suffix='%(index)d/%(max)d - remain: %(remaining)d'
                      ' - %(percent).1f%% - %(eta)ds',
                      max=count)
    return progressbar


def createlogger():
    """Return logger"""
    # create logger with 'progress bar'
    logger = logging.getLogger('luns')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOGFILE)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handler to logger
    logger.addHandler(fh)
    return logger


def run_luns(args):
    """Run all luns actions"""
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
        if args.progress:
            progbar = createprogress(len(lunlistfromfile))
            logger = createlogger()
            for entry in lunlistfromfile:
                err, msg = create_lun(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Creating luns from {}".format(csvfile))
            print("#" * 79)
            for entry in lunlistfromfile:
                print(create_lun(entry)[1])
                print("=" * 79)
    elif deletelun:
        if args.progress:
            progbar = createprogress(len(lunlistfromfile))
            logger = createlogger()
            for entry in lunlistfromfile:
                err, msg = delete_lun(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Deleting luns from {}".format(csvfile))
            print("#" * 79)
            for entry in lunlistfromfile:
                print(delete_lun(entry)[1])
                print("=" * 79)
    elif listlun:
        if args.progress:
            progbar = createprogress(len(lunlistfromfile))
            logger = createlogger()
            for entry in lunlistfromfile:
                err, msg = list_lun(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Listing luns")
            print("#" * 79)
            for entry in lunlistfromfile:
                print(list_lun(entry)[1])
                print("=" * 79)
    else:
        print("#" * 79)
        print("You need to specify an option (--list, --create, --delete)")
        print("#" * 79)
    delta = datetime.now() - START
    print("Finished in {} seconds".format(delta.seconds))


args = get_args()
if args.progress:
    try:
        from progress.bar import Bar
    except ImportError as err:
        print("You need to install progress: pip install progress - Error: {}".format(err))
        exit(1)

if __name__ == "__main__":
    run_luns(args)

