#!/usr/bin/env python3

import scapy.all as net

from gi.repository import GLib

from dbus_client import DBusGPIO_Client
import itertools
import logging

class RouterMonitor(DBusGPIO_Client):
	def init(self, output, ip_ping_address='8.8.8.8', ping_timeout=2):
		super().init( [], output )
		self.ip_ping_address = ip_ping_address
		self.ping_timeout = ping_timeout
		self.ping_count = 0
		self.output_pin = self.outputs[0]
		self.output_pin_state = lambda : self.outputs_state[ self.output_pin ]
		GLib.timeout_add_seconds(60, self.ping_pong)	# Execute ping-pong function after 60seconds
		logging.info("%-40s %-25s Relay:%d, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.output_pin, self.output_pin_state()))

	def _OutputChanged(self, num, state):
		logging.info("Relays:%d, OutputState: %s" % (self.output_pin, self.output_pin_state()) )
		if (self.output_pin_state() == 1):
			GLib.timeout_add_seconds( 3, lambda: self._Off(self.output_pin) and False )

	def ping_pong(self):
		pong = net.sr1(net.IP(dst=self.ip_ping_address)/net.ICMP(), timeout=self.ping_timeout, verbose=False)
		if not (pong is None):
			logging.debug("%s is online" % (pong.src))
			self.ping_count = 0
		else:
			logging.info("Network timeout: %d" % (self.ping_count))
			self.ping_count += 1
			if (self.ping_count >= 5):
				logging.info("Reboot router...")
				self._On(self.output_pin)
				self.ping_count = 0
		return True		# Return True to be shure, that GLib restart timer function

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	router_mon = RouterMonitor(61)

	loop = GLib.MainLoop()
	loop.run()
