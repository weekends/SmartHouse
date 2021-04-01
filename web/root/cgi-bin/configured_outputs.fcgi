#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
import dbus
import json
from common import Common

bus = dbus.SystemBus()
service_gpio = bus.get_object('su.bagna.gpio', "/su/bagna/gpio")
GetOutputsState = service_gpio.get_dbus_method('GetOutputsState',  'su.bagna.gpio')
GetConfigGPIO =  service_gpio.get_dbus_method('GetConfigGPIO',  'su.bagna.gpio')

def get_name_and_fnames(str, addons='Power_On.png;Power_Off.png'):
	res = str.split('$$$')
	name = res[0]
	if (len(res)>1): addons = res[1]
#	if (len(res)>2): fname_off = res[2]
	return name, addons

def application(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

	yield Common().common_header()
	yield '<div class="blockk"><b>Управление освещением</b>&emsp;<a href="/cgi-bin/index_base_page.fcgi">Базовый вид</a><hr>\n'.encode()

	outstate = []
	for res in GetOutputsState():
		outstate.append( (int(res[0]), bool(res[1])) )

	try:
		cfg = GetConfigGPIO()
		#yield '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"><td>Управ.</td><td>№</td><td>Название</td></tr>'.encode()
		yield '<table width="100%" style=" border-radius: 5px; border-style: solid;"><tr align="center"><td>Управ.</td><td width="10%">№</td></tr>'.encode()
		for key, value in sorted(cfg['Outputs'].items(), key=lambda t: t[1]):
			#yield ("<tr align=\"center\"><td><b id=out_%s>&nbsp</b></td><td>%s</td><td align=\"left\"><b id=name_%s>%s</b></td></tr>" % (key, key, key, value)).encode()
			value, addons = get_name_and_fnames(value)
			yield ("""<tr align="center">  <td><b id=out_%s><b id=name_%s>%s</b> <b id=addons_%s>%s</b> </b></td>  <td>%s</td></tr>"""
					% (key, key, value, key, addons, key)).encode()
		yield '</table></div>'.encode()
	except:
		yield("Error getting configured data from dbus!...").encode()

	#cfg_outs = cfg['Outputs']
	#for number, state in outstate:
	#	if (str(number) in cfg_outs):
	#		yield ("\n<tr align=\"center\"><td><b id=out_%s>&nbsp</b></td><td>%s</td></tr>" % (number, cfg_outs[str(number)])).encode()
	#yield '</table></div>'.encode()

	#for parm in cfg:
	#	if (parm == 'Outputs'):

	yield """\
</center>
<script type="text/javascript">
InitTimer();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application).run()
