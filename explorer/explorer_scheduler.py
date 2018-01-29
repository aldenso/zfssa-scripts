#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Aldo Sotolongo
# Contact: aldenso@gmail.com
# Description: Schedule automatic explorer of ZFS Storage Appliance.

from __future__ import print_function, division
import os
import time
import schedule
import zfssa_explorer
#from progressbar import ProgressBar, AdaptiveETA, Bar, Percentage


def get_zfssalist():
    """Return list of yml files in current directory"""
    zfssalist = [file for file in os.listdir(os.getcwd()) if file.endswith('yml')]
    if not zfssalist:
        print('ZFSSA yaml not found in {}'.format(os.getcwd()))
        exit(1)
    return zfssalist


def launch_explorers(zfssalist):
    """Launch explorers from a zfsssa list"""
    for zfssa in zfssalist:
        args = Namespace(server=zfssa, progress=True)
        print("Explorer for '{}' launched".format(zfssa.split('.')[0]))
        zfssa_explorer.main(args)


class Namespace:
    """Class to simulate args parsed"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == "__main__":
    zfssalist = get_zfssalist()
    schedule.every().day.at("22:00").do(launch_explorers, zfssalist)
    while True:
        schedule.run_pending()
        time.sleep(1)
