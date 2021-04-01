#!/usr/bin/env python3

import ephem
from datetime import datetime, date
import tzlocal
from time import mktime

class DayNight:
	def __init__(self, lon='27.8000932', lat='53.8135229', pressure=0, horizon='0', elev=240):
		""" elev -- Geocentric height above sea level (m) """
		self.place = ephem.Observer()
		self.place.lon  = str(lon)
		self.place.lat  = str(lat)
		self.place.pressure= pressure
		self.place.horizon = horizon
		self.place.elev = elev
		self.time_zone = tzlocal.get_localzone()

	def tz_utc_or_local(self, dt, utc=True):
		if (utc): return dt
		else: return self.time_zone.fromutc(dt)

	def sunrise(self, utc=True):
		return self.tz_utc_or_local(self.place.previous_rising(ephem.Sun()).datetime(), utc)

	def sunset(self, utc=True):
		return self.tz_utc_or_local(self.place.next_setting(ephem.Sun()).datetime(), utc)

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

	print(d.sunrise(), d.sunset())
	print(d.sunrise(False).strftime("Восход: %H:%M"), d.sunset(False).strftime("%H:%M") )

	if (d.isDay()):
		print("Now is day...")
	else:
		print("Now is night...")
