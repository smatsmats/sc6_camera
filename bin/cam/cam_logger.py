#!/usr/bin/python

import yaml
import errno
import re
import string
from string import Template
import xml.parsers.expat
from stat import *
from atom import ExtensionElement
from argparse import ArgumentParser

import logging
import logging.config

class logger:
  def __init__(self):
    with open(config['Logging']['log_config'], 'rt') as f:
        self.lconfig = yaml.load(f.read())
    logging.config.dictConfig(self.lconfig)
    print "init config"

    # create logger
    self.logger = logging.getLogger('collector')

