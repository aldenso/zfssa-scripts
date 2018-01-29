#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Aldo Sotolongo
# Contact: aldenso@gmail.com
# Description: Schedule automatic explorer of ZFS Storage Appliance.

from __future__ import print_function
import os
import argparse
import time
import schedule
import zfssa_explorer


def create_parser():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Schedule zfssa explorers")
    parser.add_argument("-d", "--directory", type=str,
                        help="Directory to find Server config files (YAML)",
                        required=True)
    parser.add_argument("-t", "--time", action='append',
                        help="24Hr time where the Job should be launched",
                        required=True)
    return parser

def get_zfssalist(directory):
    """Return list of yml files in current directory"""
    files = [file for file in os.listdir(directory) if file.endswith('yml')]
    if not files:
        print('No yaml found in {}'.format(directory))
        exit(1)
    zfssalist = [os.path.join(directory, file) for file in files]
    return zfssalist


def launch_explorers(zfssalist):
    """Launch explorers from a zfsssa list"""
    for zfssa in zfssalist:
        argsforexplorer = Namespace(server=zfssa, progress=True)
        print("Explorer for '{}' launched".format(zfssa.split('.')[0]))
        zfssa_explorer.main(argsforexplorer)


class Namespace:
    """Class to simulate args parsed"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    zfssalist = get_zfssalist(args.directory)
    for schedtime in args.time:
        print(schedtime, zfssalist)
        schedule.every().day.at(schedtime).do(launch_explorers, zfssalist)
    while True:
        schedule.run_pending()
        time.sleep(1)
