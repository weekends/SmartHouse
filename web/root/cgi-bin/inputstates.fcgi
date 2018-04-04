#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json


bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
GetInputsState = service_gpio.get_dbus_method('GetInputsState',  'su.bagna.gpio')


def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

	instate = []
	for res in GetInputsState():
		instate.append( (int(res[0]), bool(res[1])) )
	sorted(instate)

	gpios_input_state_str = ''
	for number, state in instate:
		if state:
			state_str = '[' + str(number) + ',1],'
		else:
			state_str = '[' + str(number) + ',0],'
		gpios_input_state_str = gpios_input_state_str + state_str

	gpios_input_state_str = gpios_input_state_str[0:-1]

	yield gpios_input_state_str.encode('utf-8')


if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()
