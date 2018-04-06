#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding=utf-8

from datetime import datetime
import dbus
import json

import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
def set_output_encoding(codec, errors='strict'):
    import io, sys
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), errors=errors,
            line_buffering=sys.stdout.line_buffering)
set_output_encoding('utf8')

print("Content-Type: text/html\n\n")


bus = dbus.SystemBus()
service_term = bus.get_object('su.bagna.termo', '/su/bagna/termo')
service_gpio = bus.get_object('su.bagna.gpio', '/su/bagna/gpio')
temperatures   = service_term.get_dbus_method('GetTemperatures', 'su.bagna.termo')
GetInputsState = service_gpio.get_dbus_method('GetInputsState',  'su.bagna.gpio')
GetOutputsState = service_gpio.get_dbus_method('GetOutputsState',  'su.bagna.gpio')
GetConfigGPIO =  service_gpio.get_dbus_method('GetConfigGPIO',  'su.bagna.gpio')

address_to_name = {
    '28A78CD7020000E5': [1, 'На улице'],
    '28A194D702000015': [2, 'В подвале'],
    '2850E9CF020000F5': [3, 'Плата'],
    '28FFC2026D14036E': [4, 'Китайский'],
    '28AC9F6A07000016': [5, '1'],
    '2868CF6A070000C0': [6, '2'],
    '28001E6A07000031': [7, '3'],
    '2823A469070000A4': [8, '4']
}

temperatures_str = '<div class="blockk"><b>Термометры</b><hr>\n'
temperatures_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;">\n'

temperatures_sorted = []
for sensor_id, value, name in temperatures():
    #order, name = address_to_name.get(sensor_id, [100, ''])
    #temperatures_sorted.append([order, name, sensor_id, value])
	temperatures_sorted.append([0, name, sensor_id, value])

for order, name, sensor_id, value in sorted(temperatures_sorted):
    temperatures_str += u"<tr><td>%s</td><td  align='center'>%s</td><td align='right'><span id='%s'>%3.4f °C</span></td></tr>\n" % \
                        (sensor_id, name, sensor_id, value)
temperatures_str += '</table></div>'

cfg = GetConfigGPIO()
cfg_inputs = cfg['Inputs']
instate = []
for res in GetInputsState():
    instate.append( (int(res[0]), bool(res[1])) )
sorted(instate)

outstate = []
for res in GetOutputsState():
    outstate.append( (int(res[0]), bool(res[1])) )
sorted(outstate)
cfg_outputs = cfg['Outputs']

i = 0
gpios_input_state_str = '<div class="blockk"><b>Состояние входов</b><hr>\n'
gpios_input_state_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"> <td>&nbsp</td><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td> </tr>'
for number, state in instate:
    if i == 0:
        gpios_input_state_str += '<tr align="center"><td align="left">%03d..%03d</td>' %(number, number+7)
    i += 1
    # We only add ID here, compleate data pushed from JavaScript
    gpios_input_state_str += '<td><b id=' + str(number) + '>&nbsp</b></td>';
    if i == 8:
        i = 0
        gpios_input_state_str += '</tr>'
gpios_input_state_str += '</table></div>'


gpios_output_str = '<div class="blockk"><b>Управление выходами</b>&emsp;<a href="/cgi-bin/configured_outputs.fcgi">Освещение</a><hr>\n'
gpios_output_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"> <td>&nbsp</td><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td> </tr>'
for number, state in outstate:
	if i == 0:
		gpios_output_str += '<tr align="center"><td align="left">%03d..%03d</td>' %(number, number+7)
	i += 1

	# We only add ID here, compleate data pushed from JavaScript
	if (str(number) in cfg_outputs):
		gpios_output_str += '<td><b id=out_inuse_' + str(number) + '>&nbsp</b></td>'
	else:
		gpios_output_str += '<td><b id=out_' + str(number) + '>&nbsp</b></td>'

#	gpios_output_str += '<td><b id=out_' + str(number) + '>&nbsp</b></td>'
	if i == 8:
		i = 0
		gpios_output_str += '</tr>'
gpios_output_str += '</table></div>'


body_str = """\
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=400px">
<title>Smart House controll</title>
<link rel="stylesheet" type="text/css" href="/hsstyle.css">
<style type="text/css" media='(min-width: 810px)'>body{font-size:18px;}.blockk {width: 400px;}</style>
<style type="text/css" media="(max-width: 800px) and (orientation:landscape)">body{font-size:8px;}</style>

<script src="/js/jquery-3.1.1.min.js"></script>
<script src="/js/interactive.js"></script>

</head>
<body>

<center>
"""

datetime_str = '<div class="blockk"><b>Текущая дата/время</b><hr><p id="date">' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + '</p></div>' + \
    temperatures_str + gpios_output_str + gpios_input_state_str


end_str = """\
</center>

<script type="text/javascript">
InitTimer();

//$(document).ready(function () {
//	GetOutputsState();
//});
</script>

</body>
</html>
"""

print( body_str, datetime_str, end_str)
