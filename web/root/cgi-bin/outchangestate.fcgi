#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import cgi

bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
OutOn = service_gpio.get_dbus_method('On',  'su.bagna.gpio')
OutOff = service_gpio.get_dbus_method('Off',  'su.bagna.gpio')


def application(environ, start_response):
	form = cgi.FieldStorage(environ=environ)

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
	yield """
<html><head>
<script>
function loaded()
{
    window.setTimeout(CloseMe, 500);
}

function CloseMe() 
{
    window.close();
}
</script>
</head><body onLoad="loaded()">
"""

	if "port" not in form or "state" not in form:
		yield "<H1>Error</H1>"
		yield "Please fill in the port and state fields.</body></html>"
		return

	yield("<p>Port: %s == %s" % (form["port"].value, form["state"].value))

	try:
		port = int(form["port"].value)
		if int(form["state"].value) == 1:
			OutOn(port)
			yield "On"
		else:
			OutOff(port)
			yield "Off"
	except ValueError:
		yield "Error: "+str(port)

	yield "</body></html>"

#a = application( {'REQUEST_METHOD':'GET', 'REQUEST_SCHEME':'http', 'REQUEST_URI':'/cgi-bin/outchangestate.fcgi?port=2&state=1',  'QUERY_STRING':'port=0&state=1'}, print )
#print( list(a) )
#exit()


if __name__ == '__main__':
	from flup.server.fcgi import WSGIServer
	WSGIServer(application).run()
