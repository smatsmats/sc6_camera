#!/usr/bin/python

import httplib
import httplib2
import urllib
import urllib2
import os
import random
import sys
import dateutil.parser
from pytz import timezone
from datetime import *

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import yaml
import errno
import re
import string
from string import Template
import xml.parsers.expat
from stat import *
from atom import ExtensionElement
from argparse import ArgumentParser

#import logging
#import logging.config
import cam
from cam import config as c

#from cam_config import config
#from cam_logger import logger

#class Config:
#  def __init__(self):
#    self.config_root = yaml.load(file("/usr/local/cam/conf/config.yml"))
#    self.config = config_root['Root1']

#    with open(config['Logging']['log_config'], 'rt') as f:
#        self.lconfig = yaml.load(f.read())
#    logging.config.dictConfig(self.lconfig)
#
#    # create logger
#    self.logger = logging.getLogger('collector')
#
#    # config['Paths']['video_file']
#    #    logger.error('errno:', ioex.errno)
#    #    logger.error('err code:', errno.errorcode[ioex.errno])
#    #    logger.error('err message:', os.strerror(ioex.errno))
#    #	logger.error("WTF! %s != %s" % (search_result["snippet"]["title"], title))
#    #  logger.info("going to remove: " + id)
    

def mail_message(subj, body):
#  if not c.config['Email']['Enable']:
#    return
    
  msg = MIMEText(body)
  msg['Subject'] = subj
#  msg['From'] = c['Email']['From']
#  msg['To'] = cam.config['Email']['To']
#  s = smtplib.SMTP('localhost')
#  s.sendmail(cam.config['Email']['From'], [cam.config['Email']['To']], msg.as_string())
#  s.quit()

def main():
  mail_message("Cam Collector Started", "Collector startup %s" % datetime.now())

if __name__ == '__main__':
#  print cam.config
  print c
#  cam.logger.debug("startup")
  main()
#  cam.logger.debug("FIN")
