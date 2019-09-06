#!/usr/bin/env python3

from dbus_client import DBusGPIO_Client
import itertools
import logging


class Simple_OnOff(DBusGPIO_Client):
	""" Till input On output On and vice versa"""
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.single_output = self.outputs[0]
		self.single_output_state = lambda : self.outputs_state[ self.single_output ]
		logging.info("%-40s %-25s Switch:%s, Relays:%d, OutputState: %s" % (self.trigger_name, self.inputs, self.single_output, self.single_output_state()) )

	def _InputChanged(self, num, state):
		if (state):
			self._On(self.single_output)
		else:
			self._Off(self.single_output)

class Simple_OnOff_invert(DBusGPIO_Client):
	""" Till input On output On and vice versa"""
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.single_output = self.outputs[0]
		self.single_output_state = lambda : self.outputs_state[ self.single_output ]
#		logging.info("%-40s %-25s Switch:%s, Relays:%d, OutputState: %s" % (self.trigger_name, self.inputs, self.single_output, self.single_output_state()) )
		logging.info("%-40s %-25s Switch:%s, Relays:%d, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.inputs, self.single_output, self.outputs_state[self.single_output]) )

	def _InputChanged(self, num, state):
		self.invert_output(self.single_output)


class Trigger_OnOff(DBusGPIO_Client):
	""" Short press invert output state """
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.single_output = self.outputs[0]
		logging.info("%-40s %-25s Switch:%s, Relays:%d, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.inputs, self.single_output, self.outputs_state[self.single_output]) )

	def _ShortPress(self, num):
		self.invert_output(self.single_output)



class Trigger_OneOn_AllOff(DBusGPIO_Client):
	""" Short press invert output state """
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.single_output = self.outputs[0]
		self.get_outputs_state = lambda : { i:self.outputs_state[i] for i in self.outputs }
		logging.info("%-40s %-25s Switch:%s, Relays:%s, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.inputs, self.outputs, self.get_outputs_state()) )

	def _ShortPress(self, num):
		if (1 in self.get_outputs_state().values()):
			for output, state in self.get_outputs_state().items():
				if (state == 1): self._Off(output)
		else:
			self._On(self.outputs[0])



class LongPress_Off(DBusGPIO_Client):
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.get_outputs_state = lambda : { i:self.outputs_state[i] for i in self.outputs }
		logging.info("%-40s %-25s Switch:%s, Relay:%s, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.inputs, self.outputs, self.get_outputs_state()))

	def _LongPress(self, num):
		for output, state in self.get_outputs_state().items():
			if (state == 1): self._Off(output)



class LongPress_On(DBusGPIO_Client):
	def init(self, inputs, outputs):
		super().init( inputs, outputs )
		self.get_outputs_state = lambda : { i:self.outputs_state[i] for i in self.outputs }
		logging.info("%-40s %-25s Switch:%s, Relay:%s, OutputState: %s" % (self.trigger_name, self.__class__.__name__, self.inputs, self.outputs, self.get_outputs_state()))

	def _LongPress(self, num):
		for output, state in self.get_outputs_state().items():
			if (state == 0): self._On(output)

