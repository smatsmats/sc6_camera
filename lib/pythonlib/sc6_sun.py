#!/usr/bin/python3

import time
from datetime import datetime
from datetime import timedelta
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
        self.dt_epoch = int(time.mktime(self.dt.timetuple()))
        return(self.dt)

    def set_dt(self, dt):
        self.dt = dt
        self.logger.debug("explicitly set time to {}".format(self.dt))
        return(self.dt)

    def new_times(self):
        self.get_dt()

        self.naut = sun(observer=self.place.observer,
                        date=datetime.date(self.dt),
                        dawn_dusk_depression=abs(float(self.angle_nautical)),
                        tzinfo=self.place.timezone)
        self.naut_dawn = self.naut['dawn']
        self.naut_dusk = self.naut['dusk']
        self.sun_message = "Sunrise / Sunset times:\n"
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

    # this is where we do a new dt
    def maybenewday(self):
        old_dt = self.dt
        self.get_dt()
        if self.dt.date != old_dt.date:
            self.new_times()
        return(self.dt)

    # do we want to do a get_dt here?  it makes the testing harder
    def is_sun(self):
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
        hour_after = self.end + timedelta(hours=1)
        if self.dt >= self.end and self.dt <= hour_after:
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


if __name__ == '__main__':

    mysun = SC6Sun()
    mysun.maybenewday()

    print(mysun.sun_message)
    print("NOW: ", str(mysun.dt))
    print("We'll start the party at ", str(mysun.start))
    print("We'll close shop at ", str(mysun.end))
    print("is_sun: ", mysun.is_sun(), "")
    print("is_after_sunrise: ", mysun.is_after_sunrise(), "")
    print("is_after_noon: ", mysun.is_after_noon(), "")
    print("is_after_sunset: ", mysun.is_after_sunset(), "")
    print("is_hour_after_dusk: ", mysun.is_hour_after_dusk(), "")

    # two testing things
    print("\nTesting:")
    dt = mysun.get_dt()
    noon = datetime(dt.year, dt.month, dt.day, 12, 0, 0, 0,
                    pytz.timezone(mysun.tzname))
    print(str(noon))
    mysun.set_dt(noon)
    print("sun up at noon: {}".format(mysun.is_sun()))

    dt = mysun.get_dt()
    midnight = datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0,
                        pytz.timezone(mysun.tzname))
    print(str(midnight))
    mysun.set_dt(midnight)
    print("sun up at midnight: {}".format(mysun.is_sun()))
