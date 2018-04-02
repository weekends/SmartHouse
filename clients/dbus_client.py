#!/usr/bin/env python3

import dbus
import dbus.mainloop.glib
from gi.repository import GLib, Gio, GObject

import time
import datetime
import json
import argparse
import daemon

import os
import sys
import psutil

import logging
#logging.basicConfig(level = logging.INFO)


class DBusGPIO_Client(object):
	dbus_bus_name    = 'su.bagna.gpio'
	dbus_interface   = 'su.bagna.gpio'
	dbus_object_path = "/su/bagna/gpio"

	def __init__(self, *args, auto_restart=False, **kwargs):
		self.auto_restart = auto_restart
		self.inputs = []
		self.outputs = []
		self.outputs_state = {}
		self.init_dbus()
		for num, state in  self._GetOutputsState():
			self.outputs_state[num] = state
		self.init(*args, **kwargs)

	def init(self):
		pass

	def init_dbus(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SystemBus()

		not_connected = True
		while not_connected:
			#if (dbus.SystemBus().name_has_owner(self.dbus_interface)):
			try:
				self.dbus_proxy       = self.bus.get_object(self.dbus_bus_name, self.dbus_object_path)
				self._quit            = self.dbus_proxy.get_dbus_method('Quit',            self.dbus_interface)
				self._On              = self.dbus_proxy.get_dbus_method('On',              self.dbus_interface)
				self._Off             = self.dbus_proxy.get_dbus_method('Off',             self.dbus_interface)
				self._GetOutputs      = self.dbus_proxy.get_dbus_method('GetOutputs',      self.dbus_interface)
				self._GetInputs       = self.dbus_proxy.get_dbus_method('GetInputs',       self.dbus_interface)
				self._GetOutputState  = self.dbus_proxy.get_dbus_method('GetOutputState',  self.dbus_interface)
				self._GetOutputsState = self.dbus_proxy.get_dbus_method('GetOutputsState', self.dbus_interface)
				self._GetInputState   = self.dbus_proxy.get_dbus_method('GetInputState',   self.dbus_interface)
				self._GetInputsState  = self.dbus_proxy.get_dbus_method('GetInputsState',  self.dbus_interface)

				self.dbus_proxy.connect_to_signal("InputChanged", self.InputChanged)
				self.dbus_proxy.connect_to_signal("LongPress",    self.LongPress)
				self.dbus_proxy.connect_to_signal("ShortPress",   self.ShortPress)
				self.dbus_proxy.connect_to_signal("OutputChanged",self.OutputChanged)

				if (self.auto_restart):
					self.bus.add_signal_receiver(self.NameOwnerChanged, dbus_interface="org.freedesktop.DBus", signal_name="NameOwnerChanged")
					logging.info("Auto reloading when DBus server restart turned On.")

				not_connected = False
			except Exception as e:
				logging.error(e)
				time.sleep(1)

	def NameOwnerChanged(self, name, new_owner, old_owner ):
		if (name == self.dbus_interface):
			if (new_owner != ''):
				logging.info("DBus GPIO provider service '" + self.dbus_interface + "' Down...")
			else:
				logging.info("DBus GPIO provider service '" + self.dbus_interface + "' Up...")
				self.restart_program()

	def restart_program(self):
		"""Restarts the current program, with file objects and descriptors cleanup"""
		logging.info("Restart program...")
		try:
			p = psutil.Process(os.getpid())
			for handler in p.open_files() + p.connections(kind='all'):
				os.close(handler.fd)
		except Exception as e:
			logging.error(e)
		python = sys.executable
		os.execl(python, python, *sys.argv)


	def InputChanged(self, num, state):
		if num in self.inputs:
			logging.info("Input %d state changed to: %d" % (num, state) )
			self._InputChanged(num, state)

	def ShortPress(self, num):
		if num in self.inputs:
			logging.info("Short press detected: %d" % num)
			self._ShortPress(num)

	def LongPress(self, num):
		if num in self.inputs:
			logging.info("Long press detected: %d" % num)
			self._LongPress(num)

	def OutputChanged(self, num, state):
		if num in self.outputs:
			logging.info("Output %d switch to: %s" % (num, state))
			self.outputs_state[num] = state

	def _InputChanged(self, num, state):
		pass

	def _ShortPress(self, num):
		pass

	def _LongPress(self, num):
		pass


	def run(self):
		loop = GLib.MainLoop()
		loop.run()
