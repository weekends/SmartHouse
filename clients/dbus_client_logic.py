#!/usr/bin/env python3

from dbus_client import DBusGPIO_Client
import itertools
import logging


class Simple_OnOff(DBusGPIO_Client):
	""" Till input On output On and vice versa"""
	def init(self, inputs, outputs):
		self.inputs = list(itertools.chain(*[ inputs ]))
		self.outputs = list(itertools.chain(*[ outputs ]))
		self.single_output = self.outputs[0]
		self.single_output_state = lambda : self.outputs_state[ self.single_output ]
		logging.info("Switch:%s, Relays:%d, OutputState: %s" % (self.inputs, self.single_output, self.single_output_state()) )

	def _InputChanged(self, num, state):
		if (state):
			self._On(self.single_output)
		else:
			self._Off(self.single_output)


class Trigger_OnOff(DBusGPIO_Client):
	""" Short press invert output state """
	def init(self, inputs, outputs):
		self.inputs = list(itertools.chain(*[ inputs ]))
		self.outputs = list(itertools.chain(*[ outputs ]))
		self.single_output = self.outputs[0]
		self.single_output_state = lambda : self.outputs_state[ self.single_output ]
		logging.info("Switch:%s, Relays:%d, OutputState: %s" % (self.inputs, self.single_output, self.single_output_state()) )

	def _ShortPress(self, num):
		if (self.single_output_state() == False):
			self._On(self.single_output)
		else:
			self._Off(self.single_output)

class Trigger_Bathroom(DBusGPIO_Client):
	""" Short press invert output state """
	def init(self, inputs, outputs):
		self.inputs = list(itertools.chain(*[ inputs ]))
		self.outputs = list(itertools.chain(*[ outputs ]))
		self.get_output_state1 = lambda :self._GetOutputState(self.outputs[0])
		self.get_output_state2 = lambda :self._GetOutputState(self.outputs[1])
		self.current_output_state1 = self.get_output_state1()
		self.current_output_state2 = self.get_output_state2()
		logging.info("Switch:%s, Relays:%s, OutputState: %s,%s" % (self.inputs, self.outputs, self.current_output_state1, self.current_output_state2))

	def _ShortPress(self, num):
		output_state_1 = self.get_output_state1()
		output_state_2 = self.get_output_state2()
		if (num == self.inputs[0]):
			if ((output_state_1 == 1) or (output_state_2 == 1)):
				for output in self.outputs: self._Off(output)
			else:
				self._On(self.outputs[0])
		else:
			if (output_state_2 == 1): self._Off(self.outputs[1])
			else: self._On(self.outputs[1])


class Trigger_OnOff_LongOff(DBusGPIO_Client):
	def init(self, inputs, outputs):
		self.inputs  = list(itertools.chain(*[ inputs  ]))
		self.outputs = list(itertools.chain(*[ outputs ]))
		self.get_output_state = lambda :self._GetOutputState(self.outputs[0])
		logging.info("Switch:%s, Relay:%s, OutputState: %s" % (self.inputs, self.outputs, self.get_output_state()))

	def get_outputs_state(self):
		res = []
		for num, state in self._GetOutputsState():
			if num in self.outputs:
				res.append([num, state])
		return res


	def _ShortPress(self, num):
		if (self.get_output_state() == 0):
			self._On(self.outputs[0])
		else:
			self._Off(self.outputs[0])

	def _LongPress(self, num):
		for output in self.outputs:
			self._Off(output)
