#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding=utf-8

import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
def set_output_encoding(codec, errors='strict'):
    import io, sys
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), errors=errors,
            line_buffering=sys.stdout.line_buffering)
set_output_encoding('utf8')


print("Content-Type: text/html\n\n")

import dbus
bus = dbus.SystemBus()
service_term = bus.get_object('su.bagna.termo', '/su/bagna/termo')
service_gpio = bus.get_object('su.bagna.gpio', '/su/bagna/gpio')
temperatures   = service_term.get_dbus_method('GetTemperatures', 'su.bagna.termo')
GetInputsState = service_gpio.get_dbus_method('GetInputsState',  'su.bagna.gpio')
GetOutputsState = service_gpio.get_dbus_method('GetOutputsState',  'su.bagna.gpio')
GetConfigGPIO =  service_gpio.get_dbus_method('GetConfigGPIO',  'su.bagna.gpio')


temperatures_str = '<div class="blockk"><b>Термометры</b><hr>\n'
temperatures_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;">\n'

temperatures_sorted = []
for sensor_id, value, name in temperatures():
	temperatures_sorted.append([0, name, sensor_id, value])

for order, name, sensor_id, value in sorted(temperatures_sorted):
    temperatures_str += u"<tr><td>%s</td><td  align='center'>%s</td><td align='right'><span id='%s'>%3.4f °C</span></td></tr>\n" % \
                        (sensor_id, name, sensor_id, value)
temperatures_str += '</table></div>'

cfg = GetConfigGPIO()
cfg_inputs = cfg['Inputs']
cfg_outputs = cfg['Outputs']

numered_table_string = str().join( map(lambda x:"<td>%d</td>"%x, range(0,8)) )


gpios_output_str = '<div class="blockk"><b>Управление выходами</b>&emsp;<a href="/cgi-bin/configured_outputs.fcgi">Освещение</a><hr>\n'
gpios_output_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"><td>&nbsp</td>'+numered_table_string+'</tr>'
for i, [number, state] in enumerate(sorted(GetOutputsState()), start=0):
	if (( i % 8) == 0): gpios_output_str += '<tr align="center"><td align="left">%03d..%03d</td>' %(number, number+7)
	if (str(number) in cfg_outputs): gpios_output_str += '<td><b id=out_inuse_' + str(number) + '>&nbsp</b></td>'
	else: gpios_output_str += '<td><b id=out_' + str(number) + '>&nbsp</b></td>'
	if (( (i+1) % 8) == 0): gpios_output_str += '</tr>'
gpios_output_str += '</table></div>'

gpios_input_state_str = '<div class="blockk"><b>Состояние входов</b><hr>\n'
#gpios_input_state_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"> <td>&nbsp</td>'+numered_table_string+'</tr>'
gpios_input_state_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;">'
for i, [number, state] in enumerate(sorted(GetInputsState()), start=0):
#	if (( i % 8) == 0): gpios_input_state_str += '<tr align="center"><td align="left">%03d..%03d</td>' % (number, number+7)
	if (( i % 8) == 0): gpios_input_state_str += '<tr align="center">'
	gpios_input_state_str += '<td><b id=' + str(number) + '>&nbsp</b></td>';
	if (( (i+1) % 8) == 0): gpios_input_state_str += '</tr>'
gpios_input_state_str += '</table></div>'

print("""
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=400">
<title>Smart House controll</title>
<link rel="stylesheet" type="text/css" href="/hsstyle.css">
<style type="text/css" media='(min-width: 810px)'>body{font-size:18px;}.blockk {width: 400px;}</style>
<style type="text/css" media="(max-width: 800px) and (orientation:landscape)">body{font-size:8px;}</style>

<script src="/js/jquery-3.1.1.min.js"></script>
<script src="/js/interactive.js"></script>

</head>
<body>
<center>
<div class="blockk"><b>Текущая дата/время</b><hr><p id="date">&nbsp</p></div>
""",
temperatures_str,
gpios_output_str,
gpios_input_state_str,
"""
</center>

<script type="text/javascript">
InitTimer();

//$(document).ready(function () {
//	GetOutputsState();
//});
</script>

</body>
</html>
""")
