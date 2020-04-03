#!/usr/bin/env python3

from gi.repository import GLib

from dbus_client import DBusGPIO_Client
import itertools
import logging

class Timer_Base_OffAfterPeriodOfTime(DBusGPIO_Client):
	def init(self, inputs, outputs, on_timeout=0, off_timeout=60):
		super().init(inputs, outputs)
		self.off_timeout = off_timeout
		self.timer_id = None

	def _OutputChanged(self, num, state):
		if (num == self.output_pin):
			if (self.timer_id != None):		# Output changed, remove timer, if started
				GLib.source_remove(self.timer_id)
				self.timer_id = None
			if (self.output_pin_state()):	# If Output set to On, execute new timer
				self.timer_id = GLib.timeout_add_seconds(self.off_timeout, self.time_is_up)

	def time_is_up(self):
		logging.info("%-40s %-25s TimeOut, turn Off Relays: %d" % (self.trigger_name, self.__class__.__name__, self.output_pin) )
		self.timer_id = None
		self.ExecuteWhenTimeIsUP()
		return False		# Return False to be shure, that GLib can't restart timer function

	def ExecuteWhenTimeIsUP(self):
		pass



class Timer_TimeOuted_OnOff(DBusGPIO_Client):
	""" If output state on, timeouted On output pin
		and timeouted turn off when output state off.
		output 0 == check state pin
		output 1 == output controll pi """
	def init(self, inputs, outputs, on_timeout=0, off_timeout=60):
		super().init(inputs, outputs)
		self.on_timeout = on_timeout
		self.off_timeout = off_timeout
		self.timer_id = None
		self.output_controll_pin = self.outputs[0]
		self.output_pin = self.outputs[1]
		self.output_pin_state = lambda : self.outputs_state[ self.output_pin ]
		self.output_controll_pin_state = lambda : self.outputs_state[ self.output_controll_pin ]
		logging.info("%-40s %-25s Controll pin:%s, Relays:%d, OutputState: %s, On TimeOut: %d, Off TimeOut: %d" % 
			(self.trigger_name, self.__class__.__name__, self.output_controll_pin, self.output_pin, self.outputs_state[self.output_pin], self.on_timeout, self.off_timeout) )

	def _OutputChanged(self, num, state):
		if (num == self.output_controll_pin):
			if (self.timer_id != None):     # Output changed, remove timer, if started
				GLib.source_remove(self.timer_id)
				self.timer_id = None

			if (self.output_controll_pin_state()):
				self.timer_id = GLib.timeout_add_seconds(self.on_timeout, self.ExecuteWhenTimeIsUP_On)
			else:
				self.timer_id = GLib.timeout_add_seconds(self.off_timeout, self.ExecuteWhenTimeIsUP_Off)

	def _InputChanged(self, num, state):
		pass

	def ExecuteWhenTimeIsUP_On(self):
		logging.info("%-40s %-25s TimeOut, turn On Relays: %d" % (self.trigger_name, self.__class__.__name__, self.output_pin) )
		self.timer_id = None
		self._On(self.output_pin)

	def ExecuteWhenTimeIsUP_Off(self):
		logging.info("%-40s %-25s TimeOut, turn Off Relays: %d" % (self.trigger_name, self.__class__.__name__, self.output_pin) )
		self.timer_id = None
		self._Off(self.output_pin)



class Timer_Simple_OnOff_invert(Timer_Base_OffAfterPeriodOfTime):
	""" When state changed, invert output. Also turn off by timer """
	def init(self, inputs, outputs, on_timeout=0, off_timeout=60):
		super().init( inputs, outputs, off_timeout)
		self.output_pin = self.outputs[0]
		self.output_pin_state = lambda : self.outputs_state[ self.output_pin ]
		logging.info("%-40s %-25s Switch:%s, Relays:%d, OutputState: %s, TimeOut: %d" % 
			(self.trigger_name, self.__class__.__name__, self.inputs, self.output_pin, self.outputs_state[self.output_pin], self.off_timeout) )
		self._OutputChanged(self.output_pin, self.output_pin_state)

	def _InputChanged(self, num, state):
		self.invert_output(self.output_pin)

	def ExecuteWhenTimeIsUP(self):
		self._Off(self.output_pin)




if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	router_mon = Timer_TimeOuted_OnOff([], [40, 46], on_timeout=5, off_timeout=10)

	loop = GLib.MainLoop()
	loop.run()
