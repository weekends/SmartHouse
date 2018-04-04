#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

import dbus
import cgi
from html import escape

bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
OutOn = service_gpio.get_dbus_method('On',  'su.bagna.gpio')
OutOff = service_gpio.get_dbus_method('Off',  'su.bagna.gpio')


def application(environ, start_response):
	form = cgi.FieldStorage(environ=environ)

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

	yield "<html><head></head><body onLoad=\"loaded()\">"

	if not (("port" in form) and ("state" in form)):
		yield "<H1>Error</H1>Please fill the port and state fields.</body></html>"
		return

	try:
		port = int(form["port"].value)
		if int(form["state"].value) == 1:
			OutOn(port)
			yield "On"
		else:
			OutOff(port)
			yield "Off"
	except ValueError:
		yield("Error: port='%s', state='%s'" % (form["port"].value, form["state"].value))

	yield("<p>Port: %s == %s" % (form["port"].value, form["state"].value))
	yield "</body></html>"

#a = application( {'REQUEST_METHOD':'GET', 'REQUEST_SCHEME':'http', 'REQUEST_URI':'/cgi-bin/test3.fcgi?port=2&state=0',  'QUERY_STRING':'port=2&state=0'}, print )
#print( list(a) )
#exit()

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application).run()
