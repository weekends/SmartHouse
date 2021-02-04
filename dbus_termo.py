#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

import glob
import dbus
import dbus.service
import dbus.mainloop.glib

from pyownet import protocol

import threading
import time

#import gobject
#import gi.repository.GLib
from gi.repository import GLib, Gio, GObject

import logging

Logger = logging.getLogger('sysfs.termo')
Logger.addHandler(logging.StreamHandler())
Logger.setLevel(logging.WARNING)

CFG_FILE='/etc/SmartHouse_termo.ini'


class OWTermo(object):
	OWTermTypeCodes = ['28']
	owproxy = []
	addresses = {}
	timeout = 0

	def __init__(self, owservers=['localhost:4304']):
		for owserver in owservers:
			(host, port) = owserver.split(':')
			owproxy = protocol.proxy(host=host, port=port, persistent=False)
			timeout = int( owproxy.read('/settings/timeout/volatile').decode('ascii') )
			self.owproxy.append(owproxy)
			if (self.timeout < timeout): self.timeout = timeout

	def get_addresses(self): return self.addresses
	def get_timeout(self): return self.timeout

	def read_addresses(self):
		for owproxy in self.owproxy:
			for owdir in owproxy.dir('/', bus=False):
				address = owproxy.read(owdir+'address', timeout=3).decode('ascii')
				if (address[:2] in self.OWTermTypeCodes):
					self.addresses[address] = (owproxy, owdir)
		return self.addresses

	def get_path(self, address): return self.addresses[address][1]

	def get_value(self, address):
		if address in self.addresses:
			try:
				return float( self.addresses[address][0].read(self.get_path(address)+'temperature').decode('ascii') )
			except:
				logging.error("Error reading temperature from address: %s" % address)
		return 255.0

	def get_values(self):
		res = []
		self.read_addresses()
		for address in self.addresses:
			res.append( [address, self.get_value(address)] )
		return res

	def set_name(self, address, name):
		if address in self.addresses:
			try:
				self.addresses[address][0].write(self.get_path(address)+'alias', name.encode('ascii'))
			except:
				logging.error("Error setting name '%s' for address: %s" % (name, address))




class Service(dbus.service.Object):
	def __init__(self, ow):
		self.temperatures = []
		self.terms = []
		self.ow = ow
		logging.info("Update interval: %ssec" % self.ow.get_timeout())
		for addr in self.ow.get_addresses():
			logging.info(addr, get_termometer_name(addr))

	def execute_temperature_measurment(self):
		Gio.io_scheduler_push_job(self.temperature_measurment, None, GLib.PRIORITY_DEFAULT, None)

	def temperature_measurment(self, job, cancellable, user_data):
		res = []
		for addr, temp in self.ow.get_values():
			res.append( (addr, temp, get_termometer_name(addr)) )

		if res == []:
			res.append( ("0000000000000000", 0, "Fake") )
		self.temperatures = res
		self.Temperatures(self.temperatures)

		time.sleep(self.ow.get_timeout())
		self.execute_temperature_measurment()
		return False

	def run(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SystemBus()
		self.bus_name = dbus.service.BusName("su.bagna.termo", self.bus)
		dbus.service.Object.__init__(self, self.bus_name, "/su/bagna/termo")

		self.execute_temperature_measurment()

		self._loop = GLib.MainLoop()
		logging.info("Service running...")
		self._loop.run()
		logging.info("Service stopped")

	@dbus.service.method("su.bagna.termo", in_signature='', out_signature='v')
	def GetTemperatures(self):
		return dbus.Array(self.temperatures)

	@dbus.service.method("su.bagna.termo", in_signature='s', out_signature='d')
	def GetTemperature(self, address):
		for addr, temp in self.temperatures:
			if addr == address:
				return temp
		return 0xFFFF

	@dbus.service.method("su.bagna.termo", in_signature='', out_signature='')
	def InquiryTemperatures(self):
		self.Temperatures(self.temperatures)

	@dbus.service.method("su.bagna.termo", in_signature='', out_signature='d')
	def GetTimeout(self):
		return self.ow.get_timeout()


#	@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='v')   # Retrieve GPIO's configuration
#	def GetConfigGPIO(self):
#		import configparser as ConfigParser
#		cfg = ConfigParser.ConfigParser(inline_comment_prefixes=('#','//'))
#		cfg.read(CFG_FILE)
#		result = {}
#		for key in cfg:
#			parm = {}
#			for item, value in cfg.items(key):
#				parm[item] = value
#			result[key] = parm
#
#		return dbus.Dictionary(result)


	@dbus.service.signal('su.bagna.termo')
	def Temperatures(self, temperatures):
		return str(self.temperatures)



if __name__ == "__main__":
	import configparser as ConfigParser
	cfg = ConfigParser.ConfigParser(inline_comment_prefixes=('#','//'))
	cfg.read(CFG_FILE)
	servers_list = list( (value) for item, value in cfg.items('OWServers') )
	get_termometer_name = lambda addr: cfg.get('Termometers', addr) if cfg.has_option('Termometers', addr) else ''

	ow = OWTermo(servers_list)

	is_new_names = False
	for addr in ow.read_addresses():
		if not cfg.has_option('Termometers', addr):
			cfg.set('Termometers', addr, '')
			is_new_names = True
	if (is_new_names == True):
		with open(CFG_FILE+'.generated.ini', 'w') as configfile:
			cfg.write(configfile)


	Service(ow).run()
