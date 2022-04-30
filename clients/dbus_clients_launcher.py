#!/usr/bin/env python3
#coding:utf-8

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
logging.basicConfig(level = logging.INFO, datefmt='%Y/%m/%d %H:%M:%S', format='%(message)s')
#logging.basicConfig(level = logging.INFO, datefmt='%Y/%m/%d %H:%M:%S', format='%(asctime)s %(message)s')


threads = {}
functions = []

def Start_Function(function):
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


def execute_Triggers(config):
	import dbus_client_logic as DCL
#	import dbus_network_monitor as NetMon
	import dbus_timers as Timers

	import configparser as ConfigParser
	cfg = ConfigParser.ConfigParser(inline_comment_prefixes=('#','//'))
	cfg.read(config)

	get_list = lambda val: list( eval(val) if isinstance(eval(val), (list, tuple)) else [eval(val)] )
	for section in cfg.sections():
		function_str = ''
		section_type = cfg.get(section, 'Type', fallback='Trigger')
		if (section_type == 'Trigger'):
			trigger = cfg.get(section, 'Trigger')
			inputs  = get_list( cfg.get(section, 'Inputs') )
			outputs = get_list( cfg.get(section, 'Outputs') )
			function_str = 'DCL.'+ trigger+'('+ str(inputs) +','+ str(outputs) +', trigger_name="'+ section +'").run'
		elif (section_type == 'TTrigger'):
			trigger = cfg.get(section, 'TTrigger')
			if (cfg.get(section, 'Inputs', fallback=None) != None):
				inputs  = get_list( cfg.get(section, 'Inputs') )
			else:
				inputs = []
			outputs = get_list( cfg.get(section, 'Outputs') )
			timeout_on = cfg.get(section, 'TimeOut_On', fallback="0")
			timeout_off = cfg.get(section, 'TimeOut_Off', fallback="60")
			if (trigger == 'Timer_TimeOuted_Off_DayNight'):
				timeout_off_day = cfg.get(section, 'TimeOut_Off_Day', fallback=timeout_off)
				long_press_input= cfg.get(section, 'LongPress_Input', fallback="-1")
				function_str =  'Timers.'+ trigger+'('+ str(inputs) +','+ str(outputs) +','+ timeout_off +','+ timeout_off_day +\
								', long_press_input='+str(long_press_input) +\
								', trigger_name="'+ section +'").run'
			else:
				function_str = 'Timers.'+ trigger+'('+ str(inputs) +','+ str(outputs) +','+ timeout_on +','+ timeout_off +', trigger_name="'+ section +'").run'
		elif (section_type == 'RouterMonitor'):
			output = cfg.get(section, 'Output')
			ip_ping_address = cfg.get(section, 'PingAddress', fallback='8.8.8.8')
			ping_timeout = cfg.get(section, 'PingTimeout', fallback=2)
			no_net_count = cfg.get(section, 'NoNetCount', fallback=3)
			function_str = 'NetMon.'+'RouterMonitor'+'('+ str(output) +\
														', trigger_name="'+ section + '"' +\
														', ip_ping_address="' + ip_ping_address + '"' +\
														', ping_timeout=' + str(ping_timeout) +\
														', no_net_count=' + str(no_net_count) + ').run'
		else:
			logging.info("Unknown section type: '%s'" % section_type)

		if (function_str != ''):
			try:
				functions.append( eval( function_str ) )
			except:
				logging.error("Can't execute triger: " + function_str)

	map(Start_Function, functions)  # Execute all functions in functions list


def execute(config):
	execute_Triggers(config)

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SystemBus()
	bus.add_signal_receiver(NameOwnerChanged, dbus_interface="org.freedesktop.DBus", signal_name="NameOwnerChanged")

	GLib.timeout_add(1000, ThreadsChecker() )

	loop = GLib.MainLoop()
	loop.run()



if __name__ == "__main__":
	config_file='/etc/SmartHouse_clients.ini'
	parser = argparse.ArgumentParser(description='SmartHouse clients executor')
	parser.add_argument('--daemon', '-d', action='store_true', help='Run in daemon mode')
	parser.add_argument('--config', '-c', dest='config', type=str, default=config_file, help='Config file, default config '+config_file)
	args = parser.parse_args()

	if args.daemon:
		with daemon.DaemonContext():
			execute(args.config)
	else:
		execute(args.config)
