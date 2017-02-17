#!/usr/bin/python

import os
import sys

import yaml

config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
config = config_root['Root1']
print "init config"

