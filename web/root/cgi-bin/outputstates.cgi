#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json

bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
GetOutputsState = service_gpio.get_dbus_method('GetOutputsState',  'su.bagna.gpio')

outstate = []
for res in GetOutputsState():
    outstate.append( (int(res[0]), bool(res[1])) )

sorted(outstate)

gpios_outputs_str = ''
for number, state in outstate:
    if state:
        state_str = '[' + str(number) + ',1],'
    else:
        state_str = '[' + str(number) + ',0],'
    gpios_outputs_str = gpios_outputs_str + state_str

gpios_outputs_str = gpios_outputs_str[0:-1]

print("""\
Content-Type: text/html

""")

print(gpios_outputs_str)

