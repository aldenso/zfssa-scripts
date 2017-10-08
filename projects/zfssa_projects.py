#!/usr/bin/python
# -*- coding: utf-8 -*-
# @CreateTime: Jun 18, 2017 1:13 PM
# @Author: Aldo Sotolongo
# @Contact: aldenso@gmail.com
# @Last Modified By: Aldo Sotolongo
# @Last Modified Time: Jun 18, 2017 3:45 PM
# @Description: Modify Here, Please

from __future__ import print_function, division
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
LOGFILE = "projects_output.log"


def create_parser():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Script to handle projects in ZFS Storage Appliance")
    parser.add_argument(
        "-s", "--server", type=str, help="Server config file (YAML)", required=True)
    parser.add_argument(
        "-f", "--file", type=str, help="projects file (CSV)", required=True)
    parser.add_argument(
        "-p", "--progress", action="store_true", help="progress bar and logging to file",
        required=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--create", action="store_true",
                       help="Create projects specified in csv file")
    group.add_argument("-d", "--delete", action="store_true",
                       help="Delete projects specified in csv file")
    group.add_argument("-l", "--list", action="store_true",
                       help="List/Check projects specified in csv file")
    return parser


def read_project_file(filename):
    """Read projects csv file and return the list."""
    projectlist = []
    with open(filename, 'r') as cvsfile:
        filereader = csv.reader(cvsfile, delimiter=',')
        for row in filereader:
            projectlist.append(row)
    del projectlist[0]
    return projectlist


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


def create_project(fileline):
    """Create Project from csv file. (err, msg)"""
    if len(fileline) != 20:
        return True, "CREATE - FAIL - Error in line {} It needs to be 20 columns long"\
                     .format(fileline)
    pool, project, mountpoint, quota, reservation, compression, dedup, logbias, nodestroy,\
    recordsize, readonly, atime, default_sparse, default_user, default_group, default_permissions,\
    default_volblocksize, default_volsize, sharenfs, sharesmb = fileline
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects"\
                    .format(pool)
    # converted_size = get_real_size(size, size_unit)
    # real_blocksize = get_real_blocksize(blocksize)
    try:
        data = {"name": project,
                "mountpoint": mountpoint,
                "quota": quota,
                "reservation": reservation,
                "compression": compression,
                "dedup": dedup,
                "logbias": logbias,
                "nodestroy": nodestroy,
                "recordsize": recordsize,
                "readonly": readonly,
                "atime": atime,
                "default_sparse": default_sparse,
                "default_user": default_user,
                "default_group": default_group,
                "default_permissions": default_permissions,
                "default_volblocksize": default_volblocksize,
                "default_volsize": default_volsize,
                "sharenfs": sharenfs,
                "sharesmb": sharesmb}
        if quota == 'None' and reservation == 'None':
            del data["quota"]
            del data["reservation"]
        elif quota == 'None':
            del data["quota"]
        elif reservation == 'None':
            del data["reservation"]
        req = requests.post(fullurl, data=json.dumps(data),
                            auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        if 'fault' in j:
            if 'message' in j['fault']:
                return True, "CREATE - FAIL - project '{}' pool '{}' - Error {}"\
                             .format(project, pool, j['fault']['message'])
        req.close()
        req.raise_for_status()
        return False, "CREATE - SUCCESS - project '{}' pool '{}'".format(project, pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("CREATE - FAIL - project '{}' pool '{}' - Error {}".format(project, pool,
                                                                            error.message))
        else:
            return True, "CREATE - FAIL - project '{}' pool '{}' - Error {}"\
                         .format(project, pool, error.message)
    except ConnectionError as error:
        return True, "CREATE - FAIL - project '{}' pool '{}' - Error {}"\
                     .format(project, pool, error.message)


def delete_project(fileline):
    """Delete project specified in csv file (err, msg)"""
    if len(fileline) != 2:
        return True, "DELETE - FAIL - Error in line {} It needs to be 2 columns long"\
                     .format(fileline)
    pool, project = fileline
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}".format(pool, project)
    try:
        req = requests.delete(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        req.close()
        req.raise_for_status()
        return False, "DELETE - SUCCESS - project '{}' pool '{}'".format(project, pool)
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("DELETE - FAIL - project '{}' pool '{}' - Error {}".format(project, pool,
                                                                             error.message))
        else:
            return True, "DELETE - FAIL - project '{}' pool '{}' - Error {}"\
                         .format(project, pool, error.message)
    except ConnectionError as error:
        return True, "DELETE - FAIL - project '{}' pool '{}' - Error {}"\
                     .format(project, pool, error.message)


def list_projects(fileline):
    """List/Show projects specified in csv file (err, msg)"""
    pool = project = None
    if len(fileline) == 2:
        pool, project = fileline
    elif len(fileline) == 20:
        pool, project, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = fileline
    else:
        return True, "LIST - FAIL - Error in line {} It needs to be 2 or 20 columns long"\
                     .format(fileline)
    fullurl = ZFSURL + "/storage/v1/pools/{}/projects/{}".format(pool, project)
    try:
        req = requests.get(fullurl, auth=ZAUTH, verify=False, headers=HEADER)
        j = json.loads(req.text)
        req.close()
        req.raise_for_status()
        return False, "LIST - PRESENT - project '{}' pool '{}' mountpoint '{}' quota '{}' "\
                      "reservation '{}' compression '{}' dedup '{}' logbias '{}' nodestroy '{}' "\
                      "recordsize '{}' readonly '{}' atime '{}' def_sparse '{}' def_user '{}' "\
                      "def_group '{}' def_perms '{}' def_volblocksize '{}' def_volsize '{}' "\
                      "sharenfs '{}' sharesmb '{}'"\
                      .format(j["project"]["name"],
                              j["project"]["pool"],
                              j["project"]["mountpoint"],
                              response_size(j["project"]["quota"]),
                              response_size(j["project"]["reservation"]),
                              j["project"]["compression"],
                              j["project"]["dedup"],
                              j["project"]["logbias"],
                              j["project"]["nodestroy"],
                              response_size(j["project"]["recordsize"]),
                              j["project"]["readonly"],
                              j["project"]["atime"],
                              j["project"]["default_sparse"],
                              j["project"]["default_user"],
                              j["project"]["default_group"],
                              j["project"]["default_permissions"],
                              response_size(j["project"]["default_volblocksize"]),
                              response_size(j["project"]["default_volsize"]),
                              j["project"]["sharenfs"],
                              j["project"]["sharesmb"])
    except HTTPError as error:
        if error.response.status_code == 401:
            exit("LIST - FAIL - project '{}', pool '{}' - Error {}".format(project, pool,
                                                                           error.message))
        else:
            return True, "LIST - FAIL - project '{}' pool '{}' - Error {}"\
                         .format(project, pool, error.message)
    except ConnectionError as error:
        return True, "LIST - FAIL - project '{}' pool '{}' - Error {}"\
                        .format(project, pool, error.message)


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
    logger = logging.getLogger('projects')
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
    """Run all projects actions"""
    csvfile = args.file
    listprojects = args.list
    createproject = args.create
    deleteproject = args.delete
    projectlistfromfile = read_project_file(csvfile)
    configfile = args.server
    config = read_yaml_file(configfile)
    global ZFSURL, ZAUTH
    ZFSURL = "https://{}:215/api".format(config['ip'])
    ZAUTH = (config['username'], config['password'])
    if createproject:
        if args.progress:
            progbar = createprogress(len(projectlistfromfile))
            logger = createlogger()
            for entry in projectlistfromfile:
                err, msg = create_project(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Creating projects")
            print("#" * 79)
            for entry in projectlistfromfile:
                print(create_project(entry)[1])
                print("=" * 79)
    elif deleteproject:
        if args.progress:
            progbar = createprogress(len(projectlistfromfile))
            logger = createlogger()
            for entry in projectlistfromfile:
                err, msg = delete_project(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Deleting projects")
            print("#" * 79)
            for entry in projectlistfromfile:
                print(delete_project(entry)[1])
                print("=" * 79)
    elif listprojects:
        if args.progress:
            progbar = createprogress(len(projectlistfromfile))
            logger = createlogger()
            for entry in projectlistfromfile:
                err, msg = list_projects(entry)
                if err:
                    logger.warn(msg)
                else:
                    logger.info(msg)
                progbar.next()
            progbar.finish()
        else:
            print("#" * 79)
            print("Listing projects")
            print("#" * 79)
            for entry in projectlistfromfile:
                print(list_projects(entry)[1])
                print("=" * 79)
    else:
        print("#" * 79)
        print("You need to specify an option (--list, --create, --delete)")
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