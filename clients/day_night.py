#!/usr/bin/env python3

import ephem
from datetime import datetime, date
from time import mktime

class DayNight:
	def __init__(self, lon='27.8000932', lat='53.8135229', pressure=0, horizont='-0:34', elev=240):
		self.place = ephem.Observer()
		self.place.lon  = str(lon)
		self.place.lat  = str(lat)
		self.place.pressure= 0
		self.place.horizon = '-0:34'
		self.place.elev = 240

	def isDay(self, time_delta=0):
		self.place.date = datetime.fromtimestamp( mktime( date.today().timetuple() ) + 12*60*60 )
		sunrise = self.place.previous_rising(ephem.Sun()) #Sunrise
		#noon    = self.place.next_transit(ephem.Sun(), start=sunrise) #Solar noon
		sunset  = self.place.next_setting(ephem.Sun()) #Sunset
		dt = ephem.Date( datetime.utcfromtimestamp( datetime.now().timestamp() +time_delta ) )
		#print("Test date/time in UTC: ", sunrise, dt, sunset)
		if (sunrise < dt < sunset): return True
		return False

if __name__ == "__main__":
	d = DayNight()
	if (d.isDay()):
		print("Now is day...")
	else:
		print("Now is night...")
