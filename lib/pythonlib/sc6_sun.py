#!/usr/bin/python3

from datetime import datetime
import pytz
import astral
from astral import LocationInfo
from astral.sun import sun

import argparse
# import sys
import logging
import logging.config
# import pprint
import yaml

HOUR_SECS = (60 * 60)


class SC6Sun:
    def __init__(self):
        with open('/usr/local/cam/conf/config.yml', 'r') as file:
            config_root = yaml.safe_load(file)
        config = config_root['prod']

        with open(config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)

        #  create logger
        self.logger = logging.getLogger('SC6Sun')

        self.tzname = config['General']['Timezone']
        self.get_dt()

        self.longitude = config['Sun']['Long']
        self.latitude = config['Sun']['Lat']
        self.loc_name = config['Sun']['LocationName']
        self.loc_region = config['Sun']['LocationRegion']
        self.angle_nautical = config['Sun']['AngleNautical']
        self.angle_civil = config['Sun']['AngleCivil']
        self.angle_horizon = config['Sun']['AngleHorizon']
        self.iteration = config['Sun']['Iteration']
        self.which_twilight = config['Sun']['WhichTwilight']
        self.sun_message = "Sunrise / Sunset times:\n"

        self.place = LocationInfo(self.loc_name,
                                  self.loc_region,
                                  self.tzname,
                                  self.latitude,
                                  self.longitude)
        self.logger.debug(self.place)

        self.new_times()

    def get_dt(self):
        self.dt = datetime.now(pytz.timezone(self.tzname))
        self.logger.debug("current time {}".format(self.dt))
        return(self.dt)

    def new_times(self):
        self.get_dt()

        self.naut = sun(observer=self.place.observer,
                        date=datetime.date(self.dt),
                        dawn_dusk_depression=abs(float(self.angle_nautical)),
                        tzinfo=self.place.timezone)
        self.naut_dawn = self.naut['dawn']
        self.naut_dusk = self.naut['dusk']
        self.sun_message = self.sun_message + \
            "Nautical Dawn is: " + str(self.naut_dawn) + "\n"
        self.sun_message = self.sun_message + \
            "Nautical Dusk is: " + str(self.naut_dusk) + "\n"

        self.civi = sun(observer=self.place.observer,
                        date=datetime.date(self.dt),
                        dawn_dusk_depression=abs(float(self.angle_civil)),
                        tzinfo=self.place.timezone)
        self.civi_dawn = self.civi['dawn']
        self.civi_dusk = self.civi['dusk']
        self.sun_message = self.sun_message + \
            "Civil Dawn is: " + str(self.civi_dawn) + "\n"
        self.sun_message = self.sun_message + \
            "Civil Dusk is: " + str(self.civi_dusk) + "\n"

        self.horz = sun(observer=self.place.observer,
                        date=datetime.date(self.dt),
                        dawn_dusk_depression=abs(float(self.angle_horizon)),
                        tzinfo=self.place.timezone)
        self.sunrise = self.horz['dawn']
        self.sunset = self.horz['dusk']
        self.noon = self.horz['noon']
        self.sun_message = self.sun_message + \
            "Sunrise is: " + str(self.sunrise) + "\n"
        self.sun_message = self.sun_message + \
            "Sunset is: " + str(self.sunset) + "\n"

        if self.which_twilight == 'nautical':
            self.start = self.naut_dawn
            self.end = self.naut_dusk
        elif self.which_twilight == 'civil':
            self.start = self.civi_dawn
            self.end = self.civi_dusk
        elif self.which_twilight == 'norizon':
            self.start = self.horz_dawn
            self.end = self.horz_dusk
        else:
            print("need to set which twilight to use")
            sys.exit()
        self.sun_message = self.sun_message + \
            "Start capturing at: " + str(self.start) + "\n"
        self.sun_message = self.sun_message + \
            "End capturing at: " + str(self.end) + "\n"

        self.logger.debug(self.sun_message)

#     self.noon = datetime.new(
#       year       = self.dt}.year,
#       month      = self.dt}.month,
#       day        = self.dt}.day,
#       hour       = 12,
#       minute     = 0,
#       second     = 0,
#       nanosecond = 0,
#       time_zone  = config['General']['Timezone'],
#     )

    def check4newday(self):
        old_dt = self.dt.date
        newdt = datetime.now(pytz.timezone(self.tzname))
        if self.dt.date != newdt.date:
            self.new_times()

    def is_sun(self):
        self.get_dt()

        if self.dt >= self.start and self.dt <= self.end:
            return 1
        else:
            return 0

    def start_time(self):
        return self.start

    def end_time(self):
        return self.end

    def is_hour_after_dusk(self):
        self.get_dt()
        if self.dt >= self.end and elf.dt <= self.end + HOUR_SECS:
            return 1
        else:
            return 0

    def is_after_noon(self):
        self.get_dt()
        if self.dt >= self.noon:
            return 1
        else:
            return 0

    def is_after_sunrise(self):
        self.get_dt()
        if self.dt >= self.sunrise:
            return 1
        else:
            return 0

    def is_after_sunset(self):
        self.get_dt()
        if self.dt >= self.sunset:
            return 1
        else:
            return 0


mysun = SC6Sun()
print(mysun.sun_message)
mysun.check4newday()
