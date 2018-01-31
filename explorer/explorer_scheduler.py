#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Aldo Sotolongo
# Contact: aldenso@gmail.com
# Description: Schedule automatic explorer of ZFS Storage Appliance.

from __future__ import print_function
import os
from datetime import datetime
import argparse
import time
import threading
import schedule
import inotify.adapters
import zfssa_explorer


def create_parser():
    """Get Arguments"""
    parser = argparse.ArgumentParser(
        description="Schedule zfssa explorers")
    parser.add_argument("-d", "--directory", type=str,
                        help="Directory to find Server config files (YAML)",
                        required=True)
    parser.add_argument("-t", "--time", nargs='+',
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


class ThreadingInotify(object):
    """ Threading inotify"""

    def __init__(self, directory, interval=1):
        self.directory = directory
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            i = inotify.adapters.Inotify()

            i.add_watch(self.directory)

            for event in i.event_gen(yield_nones=False):
                (_, etype, _, _) = event

                if 'IN_DELETE' in etype or 'IN_MODIFY' in etype or 'IN_MOVED_TO' in \
                etype or 'IN_MOVED_FROM' in etype or 'IN_CREATE' in etype:
                    schedule.clear()
                    print("---- Removed previous schedules ----")
                    zfssanewlist = get_zfssalist(self.directory)
                    for stime in args.time:
                        for zfs in zfssanewlist:
                            print("++++ Scheduled: {} {} ++++".format(stime, zfs))
                        schedule.every().day.at(stime).do(launch_explorers, zfssalist)

            time.sleep(self.interval)


if __name__ == "__main__":
    print("Started at: {}".format(datetime.now()))
    parser = create_parser()
    args = parser.parse_args()
    zfssalist = get_zfssalist(args.directory)
    for schedtime in args.time:
        schedule.every().day.at(schedtime).do(launch_explorers, zfssalist)
        for zfssa in zfssalist:
            print("++++ Scheduled: {} {} ++++".format(schedtime, zfssa))
    ThreadingInotify(args.directory)
    while True:
        schedule.run_pending()
        time.sleep(1)
