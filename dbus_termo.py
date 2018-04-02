#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

import glob
import dbus
import dbus.service
import dbus.mainloop.glib

import threading
import time

#import gobject
#import gi.repository.GLib
from gi.repository import GLib, Gio, GObject

import logging

Logger = logging.getLogger('sysfs.termo')
Logger.addHandler(logging.StreamHandler())
Logger.setLevel(logging.WARNING)


class Service(dbus.service.Object):
	def __init__(self, mnt_dir):
		self.temperatures = []
		self.terms = []
		for sensor_dir in sorted(glob.glob(mnt_dir + '/28*')):
			try:
				address = open(sensor_dir+"/address", 'r').read()
			except IOError as e:
				print("Error reading sensor address: %s: ErrNum:%s - %s" % (sensor_dir, e.errno, e.strerror))

			self.terms.append( (sensor_dir,  address) )
			self.temperatures.append( (address, 255) )
			print(sensor_dir, address)

#		GObject.threads_init()

	def execute_temperature_measurment(self):
		Gio.io_scheduler_push_job(self.temperature_measurment, None, GLib.PRIORITY_DEFAULT, None)

	def temperature_measurment(self, job, cancellable, user_data):
		res = []
		for sensor_dir, address in self.terms:
			val = 255
			try:
				val = float( open(sensor_dir+'/temperature', 'r').read() )
			except IOError as e:
				print("Error reading from file: %s: ErrNum:%s - %s" % (address, e.errno, e.strerror))
			except:
				print("Error reading Addr:%s value: '%s'" % (address, val))
			res.append( (address, val) )

		if res == []:
			res.append( ("Fake", 0) )
		self.temperatures = res
		self.Temperatures(self.temperatures)

		time.sleep(1)
		self.execute_temperature_measurment()
		return False


	def run(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SystemBus()
		self.bus_name = dbus.service.BusName("su.bagna.termo", self.bus)
		dbus.service.Object.__init__(self, self.bus_name, "/su/bagna/termo")

		self.execute_temperature_measurment()

		self._loop = GLib.MainLoop()
		print("Service running...")
		self._loop.run()
		print("Service stopped")

	@dbus.service.method("su.bagna.termo", in_signature='', out_signature='v')
	def GetTemperatures(self):
		return dbus.Array(self.temperatures)

	@dbus.service.method("su.bagna.termo", in_signature='s', out_signature='d')
	def GetTemperature(self, address):
		for addr, temp in self.temperatures:
			if addr == address:
				return temp
		return 0xFFFF

	@dbus.service.signal('su.bagna.termo')
	def Temperatures(self, temperatures):
		return str(self.temperatures)

	@dbus.service.method("su.bagna.termo", in_signature='', out_signature='')
	def InquiryTemperatures(self):
		self.Temperatures(self.temperatures)


if __name__ == "__main__":
	Service("/mnt/1wire").run()
