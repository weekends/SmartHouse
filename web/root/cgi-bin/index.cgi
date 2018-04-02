#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json

bus = dbus.SystemBus()
service_term = bus.get_object('su.bagna.termo', '/su/bagna/termo')
service_gpio = bus.get_object('su.bagna.gpio', '/su/bagna/gpio')
temperatures   = service_term.get_dbus_method('GetTemperatures', 'su.bagna.termo')
GetInputsState = service_gpio.get_dbus_method('GetInputsState',  'su.bagna.gpio')
GetOutputsState = service_gpio.get_dbus_method('GetOutputsState',  'su.bagna.gpio')

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
for sensor_id, value in temperatures():
    order, name = address_to_name.get(sensor_id, [100, ''])
    temperatures_sorted.append([order, name, sensor_id, value])

for order, name, sensor_id, value in sorted(temperatures_sorted):
    temperatures_str += "<tr><td>%s</td><td  align='center'>%s</td><td align='right'><span id='%s'>%3.4f °C</span></td></tr>\n" % \
                        (sensor_id, name, sensor_id, value)
temperatures_str += '</table></div>'


instate = []
for res in GetInputsState():
    instate.append( (int(res[0]), bool(res[1])) )
sorted(instate)

outstate = []
for res in GetOutputsState():
    outstate.append( (int(res[0]), bool(res[1])) )
sorted(outstate)

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


gpios_output_str = '<div class="blockk"><b>Управление выходами</b><hr>\n'
gpios_output_str += '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"> <td>&nbsp</td><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td> </tr>'
for number, state in outstate:
	if i == 0:
		gpios_output_str += '<tr align="center"><td align="left">%03d..%03d</td>' %(number, number+7)
	i += 1

	# We only add ID here, compleate data pushed from JavaScript
	gpios_output_str += '<td><b id=out_' + str(number) + '>&nbsp</b></td>'

#	gpios_output_str += '<td><b id=out_' + str(number) + '>&nbsp</b></td>'
	if i == 8:
		i = 0
		gpios_output_str += '</tr>'
gpios_output_str += '</table></div>'


print("""\
Content-Type: text/html

<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=400px">
<title>Smart House controll</title>
<link rel="stylesheet" type="text/css" href="/hsstyle.css">
<style type="text/css" media='(min-width: 810px)'>body{font-size:18px;}.blockk {width: 400px;}</style>
<style type="text/css" media="(max-width: 800px) and (orientation:landscape)">body{font-size:8px;}</style>

<style type="text/css">
    TABLE {
        /* border: 2px solid black; */ /* Рамка вокруг таблицы */
        /* border-spacing: collapse; */ /* Убираем двойные линии между ячейками */
        border-spacing:  0px 0px;; /* Убираем двойные линии между ячейками */

        border: solid 1px #2d2d2d;
        background:#0059B3;
        /* padding:10px 10px 10px 10px; */
        -moz-border-radius: 5px;
        -webkit-border-radius: 5px;
        border-radius: 5px;

        font-size: 16px;
    }
    TD, TH {
        /* text-align: left; */ /* Выравнивание по центру */
        padding: 3px; /* Поля вокруг содержимого ячеек */
        border: solid 1px #2d2d2d; /* Параметры рамки */

        -moz-border-radius: 5px;
        -webkit-border-radius: 5px;
        border-radius: 5px;
    }
    TH {
        /* background: #4682b4; */ /* Цвет фона */
        color: white; /* Цвет текста */
        border-bottom: 2px solid black; /* Линия снизу */
    }
    TD.col1 {
        color: black;
    }
    TD.col2 {
        color: blue;
        font-weight: bold;
    }
    .lc {
        font-weight: bold; /* Жирное начертание текста */
        text-align: left; /* Выравнивание по левому краю */
    }

  button {
//    color: red;
//    margin: 5px;
    width: 100%;
	padding: 0;
    margin: 0;
	background-image: none;
	background-color: transparent;
	cursor: pointer;
  }
  button:hover {
//    background: yellow;
  }
</style>


<script src="/js/jquery-3.1.1.min.js"></script>
<script src="/js/test.js"></script>

</head>
<body>

<center>
""")

print('<div class="blockk"><b>Текущая дата/время</b><hr><p id="date">' + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + '</p></div>' + \
    temperatures_str + gpios_output_str + gpios_input_state_str)

print("""\
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
