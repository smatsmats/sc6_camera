#!/usr/local/cam/env/bin/python3

import sys

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_sun

mysun = sc6_sun.SC6Sun()
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
