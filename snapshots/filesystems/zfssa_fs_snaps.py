#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: Jan 30, 2017 11:26 PM
# @Author: Aldo Sotolongo
# @Contact: aldenso@gmail.com
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: Jun 18, 2017 1:43 AM
# @Description: Create, Delete and list snapshots defined in csv file.


from __future__ import print_function
import json
import csv
from datetime import datetime
import argparse
import logging
import yaml
import requests
from requests.exceptions import HTTPError, ConnectionError
from urllib3.exceptions import InsecureRequestWarning

# to disable warning
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See:
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
requests.urllib3.disable_warnings(InsecureRequestWarning)

START = datetime.now()
ZFSURL = ""  # API URL (https://example:215/api)
ZAUTH = ()   # API Authentication tuple (username, password)
HEADER = {"Content-Type": "application/json"}
LOGFILE = "snapshots_output.log"


def create_parser():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Script to handle snapshots in ZFS Storage Appliance")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)",
        required=True)
    parser.add_argument(
        "-f", "--file", type=str, help="Snapshots file (CSV)", required=True)
    parser.add_argument(
        "-p", "--progress", action="store_true", help="progress bar and logging to file",
        required=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create", action="store_true",
                       help="Create Snapshots specified in csv file")
    group.add_argument("-d", "--delete", action="store_true",
                       help="Delete Snapshots specified in csv file")
    group.add_argument("-l", "--list", action="store_true",
                       help="List/Check Snapshots specified in csv file")
    return parser


def read_snap_file(filename):
    """Read snap csv file and return the list"""
    snaplist = []
    with open(filename, 'r') as cvsfile:
        filereader = csv.reader(cvsfile, delimiter=',')
        for row in filereader:
            snaplist.append(row)
    return snaplist


def read_yaml_file(configfile):
    """Read config file and return credentials in json."""
    config = {}
    with open(configfile, 'r') as configuration:
        try:
            config = yaml.load(configuration)
        except yaml.YAMLError as error:
            print("Error in configuration file: {}").format(error)
        return config


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def response_size(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def create_snap(snap):
    """Create Snapshots from csv file"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots".format(pool, project, filesystem)
    try:
        req = requests.post(fullurl, data=json.dumps({'name': snapname}),
                            auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        req.close()
        req.raise_for_status()
        if 'fault' in j:
            if 'message' in j['fault']:
                return True, "CREATE - FAIL - snapshot '{}' filesystem '{}' project '{}' "\
                             "pool {}' - Error {}".format(snapname, filesystem, project, pool,
                                                          j['fault']['message'])
        else:
            return False, "CREATE - SUCCESS - snapshot '{}' filesystem '{}' project '{}' "\
                          "pool '{}'".format(snapname, filesystem, project, pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("CREATE - FAIL - snapshot '{}' filesystem '{}' project '{}' "
                 "pool '{}' - Error {}".format(snapname, filesystem, project, pool,
                                               error.message))
        else:
            return True, "CREATE - FAIL - snapshot '{}' filesystem '{}' project '{}' "\
                         "pool '{}' - Error {}".format(snapname, filesystem, project, pool,
                                                       error.message)
    except ConnectionError as error:
        return True, "CREATE - FAIL - snapshot '{}' filesystem '{}' project '{}' "\
                     "pool '{}' - Error {}".format(snapname, filesystem, project, pool,
                                                   error.message)


def delete_snap(snap):
    """Delete Snapshots specified in csv file"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots/{}".format(pool, project, filesystem,
                                             snapname)
    try:
        req = requests.delete(fullurl, auth=ZAUTH, verify=False,
                              headers=HEADER)
        req.close()
        req.raise_for_status()
        return False, "DELETE - SUCCESS - snapshot '{}' filesystem '{}' project '{}' "\
                      "pool '{}'".format(snapname, filesystem, project, pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("DELETE - FAIL - snapshot '{}' filesystem '{}' project '{}' pool '{}' "\
                        "- Error {}".format(snapname, filesystem, project, pool, error.message))
        else:
            return True, "DELETE - FAIL - snapshot '{}' filesystem '{}' project '{}' pool '{}'"\
                         " - Error {}".format(snapname, filesystem, project, pool, error.message)
    except ConnectionError as error:
        return True, "DELETE - FAIL - snapshot '{}' filesystem '{}' project '{}' pool '{}' "\
                     "- Error {}".format(snapname, filesystem, project, pool, error.message)


def list_snap(snap):
    """List Snapshots specified in csv file (fail, message)"""
    pool, project, filesystem, snapname = snap
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}/filesystems/{}/"\
                       "snapshots".format(pool, project, filesystem)
    try:
        req = requests.get(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        req.close()
        req.raise_for_status()
        if len(j['snapshots']) == 0:
            return False, "LIST - NOTPRESENT - snapshot '{}' filesystem '{}' project '{}' and "\
                          "pool '{}' - Message Snapshot not present".format(snapname, filesystem,
                                                                            project, pool)
        else:
            for i in j['snapshots']:
                if i['name'] == snapname:
                    return False, "LIST - PRESENT - snapshot '{}' filesystem '{}' project "\
                                  "'{}' pool '{}' created_at '{}' space_data '{}'"\
                                  " space_unique '{}'".format(i['name'], filesystem, project,
                                                              pool, i['creation'],
                                                              response_size(i['space_data']),
                                                              response_size(i['space_unique']))
        return False, "LIST - NOTPRESENT - snapshot '{}' filesystem '{}' project '{}' pool "\
                      "'{}' - Message Snapshot not present".format(snapname, filesystem,
                                                                   project, pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("LIST - FAIL - snapshot '{}' filesystem '{}' project '{}' pool '{}' "
                 "- Error {}".format(snapname, filesystem, project, pool, error.message))
        else:
            return True, "LIST - FAIL - snapshot '{}' filesystem '{}' project '{}' pool "\
                         "'{}' - Error {}".format(snapname, filesystem, project, pool,
                                                  error.message)
    except ConnectionError as error:
        return True, "LIST - FAIL - snapshot '{}' filesystem '{}' project '{}' pool "\
                     "'{}' - Error {}".format(snapname, filesystem, project, pool, error.message)


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
    logger = logging.getLogger('snapshots')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOGFILE)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handler to logger
    logger.addHandler(fh)
    return logger


def main(args):
    """Run all snapshots actions"""
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
        if args.progress:
            progbar = createprogress(len(snaplist))
            logger = createlogger()
            for entry in snaplist:
                err, msg = create_snap(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Creating snapshots")
            print("#" * 79)
            for entry in snaplist:
                print(create_snap(entry)[1])
                print("=" * 79)
    elif deletesnaps:
        if args.progress:
            progbar = createprogress(len(snaplist))
            logger = createlogger()
            for entry in snaplist:
                err, msg = delete_snap(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Deleting snapshots")
            print("#" * 79)
            for entry in snaplist:
                print(delete_snap(entry)[1])
                print("=" * 79)
    elif listsnaps:
        if args.progress:
            progbar = createprogress(len(snaplist))
            logger = createlogger()
            for entry in snaplist:
                err, msg = list_snap(entry)
                if err:
                    logger.warning(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Listing snapshots")
            print("#" * 79)
            for entry in snaplist:
                print(list_snap(entry)[1])
                print("=" * 79)
    else:
        print("#" * 79)
        print("You need to specify a snap option (--list, --create, --delete)")
        print("#" * 79)
    delta = datetime.now() - START
    print("Finished in {} seconds".format(delta.seconds))


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    if args.progress:
        try:
            from progress.bar import Bar
        except ImportError as err:
            print("You need to install progress: pip install progress - Error: {}".format(err))
            exit(1)
    main(args)

