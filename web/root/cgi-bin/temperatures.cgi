#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json

bus = dbus.SystemBus()
service_term = bus.get_object('su.bagna.termo', "/su/bagna/termo")
temperatures   = service_term.get_dbus_method('GetTemperatures', 'su.bagna.termo')

temperatures_str = ''
for sensor_id, value in temperatures():
    temperatures_str += "[\"%s\",\"%3.4f °C\"]," % (sensor_id, value)

temperatures_str = temperatures_str[0:-1]

print("""\
Content-Type: text/html

""")

print(temperatures_str)
