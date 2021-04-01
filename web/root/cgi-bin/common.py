#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

from datetime import datetime
from day_night import DayNight

class Common:
	def __init__(self):
		dn = DayNight()
		if (dn.isDay()):
			self.day_night_str = "День"
		else:
			self.day_night_str = "Ночь"
		self.day_night_str += dn.sunrise(False).strftime(" (Восход: %H:%M") + dn.sunset(False).strftime(" Закат: %H:%M)")

	def common_header(self):
		return ("""
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
""".encode() +
		("<div class=\"blockk\"><b><p id=\"date\">%s</p></b><p>%s</p></div>" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), self.day_night_str)).encode() )

#		("<div class=\"blockk\"><b><p id=\"date\">%s</p></b><hr>%s</div>" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), self.day_night_str)).encode() )

if __name__ == '__main__':
	print( Common().common_header() )
