#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json

bus = dbus.SystemBus()
service_term = bus.get_object('su.bagna.termo', "/su/bagna/termo")
temperatures   = service_term.get_dbus_method('GetTemperatures', 'su.bagna.termo')
GetTimeout = service_term.get_dbus_method('GetTimeout', 'su.bagna.termo')

def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

	temperatures_str = ''
	for sensor_id, value, name in temperatures():
		temperatures_str += "[\"%s\",\"%3.4f °C\",\"%s\"]," % (sensor_id, value, name)

	temperatures_str = temperatures_str[0:-1]

	yield temperatures_str.encode('utf-8')


if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()
