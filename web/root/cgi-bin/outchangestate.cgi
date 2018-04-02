#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json
import cgi

bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
OutOn = service_gpio.get_dbus_method('On',  'su.bagna.gpio')
OutOff = service_gpio.get_dbus_method('Off',  'su.bagna.gpio')

print("""\
Content-Type: text/html


<html>
<head>
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
</head>

<body onLoad="loaded()">
""")

form = cgi.FieldStorage()
if "port" not in form or "state" not in form:
    print("<H1>Error</H1>")
    print("Please fill in the port and state fields.")
    exit(1)

print("<p>Port: %s == %s" % (form["port"].value, form["state"].value))

try:
    port = int(form["port"].value)
    if int(form["state"].value) == 1:
        OutOn(port)
        print("On")
    else:
        OutOff(port)
        print("Off")
except ValueError:
    print("Error: ", port)

print("</body></html>")
