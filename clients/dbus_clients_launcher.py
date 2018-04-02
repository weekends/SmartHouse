#!/usr/bin/env python3

import dbus_common as DB

import dbus
import dbus.mainloop.glib
from gi.repository import GLib, Gio, GObject

import threading
import os
import sys
import psutil

import argparse
import daemon

import logging
logging.basicConfig(level = logging.INFO)

"""
Ванная 1 этаж, выключатель в коридоре:	  173, Лампа: 47
Ванная 1 этаж, выключатель в постирочной: 185, Лампа: 38

Спальня 1 этаж, выключатель на входе 1:	164, Лампа: 54
Спальня 1 этаж, выключатель на входе 2: 168, Лампа: 52, Длинное нажатее отключает Лампу: 54
Спальня 1 этаж, выключатель по центру:	167, Лампа: 52, Длинное нажатее отключает Лампу: 54
"""

threads = {}
functions = []

def Prepare_Trigger_OnOff():
	from dbus_client_logic import Trigger_OnOff
	cfg = [
		[ [164], 54 ]
	]
	for inputs, output in cfg:
		functions.append( Trigger_OnOff( inputs, output ).run )

def Prepare_Trigger_Bathroom():
	from dbus_client_logic import Trigger_Bathroom
	functions.append( Trigger_Bathroom( [173, 185], [47, 38] ).run )

def Prepare_Trigger_OnOff_LongOff():
	from dbus_client_logic import Trigger_OnOff_LongOff
	functions.append( Trigger_OnOff_LongOff( [168, 167], [52, 54] ).run )


def Start_Functions():
	for function in functions:
		thread = threading.Thread( target=function )
		thread.start()
		threads[function] = thread

def restart_program():
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


def NameOwnerChanged(name, new_owner, old_owner ):
	if (name == DB.dbus_interface):
		if (new_owner != ''):
			logging.info("DBus GPIO provider service '" + DB.dbus_interface + "' Down...")
		else:
			logging.info("DBus GPIO provider service '" + DB.dbus_interface + "' Up...")
			restart_program()


class ThreadsChecker:
	def __init__(self):
		pass

	def __call__(self, *args):
		for function in threads:
			thread = threads[function]
			if thread.is_alive() == False:
				print(function, thread.is_alive(), thread.name)
				threads.pop(function)
				thread = threading.Thread( target=function )
				threads[function] = thread
		return True


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='SmartHouse clients executor')
	parser.add_argument('--daemon', action='store_true', help='Run in daemon mode')
	args = parser.parse_args()

	Prepare_Trigger_OnOff()
	Prepare_Trigger_Bathroom()
	Prepare_Trigger_OnOff_LongOff()
	Start_Functions()	# Execute prepared functions

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	bus.add_signal_receiver(NameOwnerChanged, dbus_interface="org.freedesktop.DBus", signal_name="NameOwnerChanged")

	GLib.timeout_add(1000, ThreadsChecker() )

	loop = GLib.MainLoop()
	loop.run()


#	if args.daemon:
#		with daemon.DaemonContext():
#			execute()
#	else:
#		execute()
