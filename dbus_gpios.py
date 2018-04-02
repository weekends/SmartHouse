#!/usr/bin/env python3

import time
from threading import Timer

import dbus
import dbus.service
import dbus.mainloop.glib

#import gi.repository.GLib
from gi.repository import GLib, Gio, GObject

import logging

Logger = logging.getLogger('sysfs.gpio')
Logger.addHandler(logging.StreamHandler())
Logger.setLevel(logging.WARNING)
#Logger.setLevel(logging.DEBUG)

from GPIO_board import GPIO_board
import PCA9555 as GPIO
#import Adafruit_GPIO.I2C as I2C
import cape_detector as capes_detector
from cape_detector import GPIOmapper

class Service(dbus.service.Object):
	dbus_bus_name    = 'su.bagna.gpio'
	dbus_interface   = 'su.bagna.gpio'
	dbus_object_path = "/su/bagna/gpio"

	timer = {}

	def __init__(self, message):
		self._message = message
		self.outputs = {}
		self.inputs = {}

		self.capes = capes_detector.CapeDetector()

		self.time_ms = lambda: int(round(time.time() * 1000))

		self.output_quantity = 0
		for cape in self.capes.get_outputs():
			i2c_addresses = cape.get_gpio_i2c_address()
			i2c_bus = cape.get_i2c_bus()
			i2c_1_addr = i2c_addresses[0][0]
			i2c_2_addr = i2c_addresses[1][0]
			slot = cape.get_slot()-1
			print(slot, cape.get_type(), cape.get_gpio_i2c_address() )
			self.outputs[slot] = GPIO_board( i2c_bus=i2c_bus, i2c_addr=[i2c_1_addr, i2c_2_addr], direction=GPIO.OUT)
			self.output_quantity += self.outputs[slot].NUM_GPIO

		self.input_quantity = 0
		for cape in self.capes.get_inputs():
			i2c_addresses = cape.get_gpio_i2c_address()
			i2c_bus = cape.get_i2c_bus()
			i2c_1_addr = i2c_addresses[0][0]
			i2c_2_addr = i2c_addresses[1][0]
			i2c_1_int = i2c_addresses[0][1]
			i2c_2_int = i2c_addresses[1][1]
			slot = cape.get_slot()-1
			print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )
			self.inputs[slot] = GPIO_board( i2c_bus=i2c_bus, i2c_addr=[i2c_1_addr, i2c_2_addr], direction=GPIO.IN, i2c_interrupt_pins=[i2c_1_int, i2c_2_int], polarity=True, callback=self.callback, slot=slot)
			self.input_quantity += self.inputs[slot].NUM_GPIO

		print("Detected %d outputs and %d inputs." % (self.output_quantity, self.input_quantity) )

	def get_list_of_changed_bits(self, before, after):
		res = []
		for bit in range(0, GPIO_board.NUM_GPIO):
			bit_before = ( before>>bit ) & 0x01
			bit_after  = ( after >>bit ) & 0x01
			if (bit_before != bit_after): res.append([bit, bit_before, bit_after])
		return res


	def generate_ShortLongEvents(self, gpio, state):
		time_diff = 0
		if (self.timer.get(gpio) != None):
			time_diff = self.time_ms() - self.timer[gpio]
			self.timer.pop(gpio)

		timer_key = str(gpio)+"lpress"
		if (self.timer.get(timer_key) != None):
			self.timer.get(timer_key).cancel()	# Terminate timer for corespondent pin
			self.timer.pop(timer_key)			# Remove LongPress timer if pin change event received

		if (state):
			self.timer[gpio] = self.time_ms()

			timer = Timer(1.0, self.LongPress, [gpio])	# Send LongPress event if button pressed more than 1.0 second(s)
			timer.start()								# Start timer for LongPress detection
			self.timer.update( {timer_key:timer} )		# Store timer info to dictionary, need to remove timer if button released
		else:
			if ((time_diff >= 100) and (time_diff <= 500)):
				#print("ShortPressEvent:", gpio)
				self.ShortPress( gpio )


	def callback(self, prev_state, cur_state, slot):
		"""
		Sending input GPIO change signal to DBus
		"""
		state = self.get_list_of_changed_bits(prev_state, cur_state)
		for gpio_number, old_state, new_state in state:
			gpio = slot*32 + gpio_number
			self.InputChanged(gpio, new_state)				# Send state change event
			self.generate_ShortLongEvents(gpio, new_state)	# Generate additional Short and Long Press events


	def run(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SystemBus()
		self.bus_name = dbus.service.BusName(self.dbus_bus_name, self.bus)
		dbus.service.Object.__init__(self, self.bus_name, self.dbus_object_path)

		self._loop = GLib.MainLoop()
		print("Service running...")
		try:
			self._loop.run()
		except:
			print("Service shutdown...")
			self._loop.quit()

	#@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='')
	#def Quit(self):
	#    print("  shutting down")
	#    self._loop.quit()

	@dbus.service.method("su.bagna.gpio", in_signature='i', out_signature='b')   # Turn GPIO On
	def On(self, num):
		res = self.outputs[ num // GPIO_board.NUM_GPIO ].set_pin( num  % GPIO_board.NUM_GPIO, True)
		if (res == True): self.OutputChanged(num, True)
		return res

	@dbus.service.method("su.bagna.gpio", in_signature='i', out_signature='b')   # Turn GPIO Off
	def Off(self, num):
		res = self.outputs[ num // GPIO_board.NUM_GPIO ].set_pin( num  % GPIO_board.NUM_GPIO, False)
		if (res == True): self.OutputChanged(num, False)
		return res

	@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='v')   # Retrieve available outputs GPIO list
	def GetOutputs(self):
		result = []
		for slot in self.outputs:
			start = slot*GPIO_board.NUM_GPIO
			result += list( range(start, start + GPIO_board.NUM_GPIO) )
		if (result == []): result = [-1]
		return dbus.Array(sorted(result))

	@dbus.service.method("su.bagna.gpio", in_signature='i', out_signature='b')   # Retrieve state of the corespondent GPIO
	def GetOutputState(self, num):
		return self.outputs[ num // GPIO_board.NUM_GPIO].get_output( num % GPIO_board.NUM_GPIO )

	@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='v')   # Retrieve output GPIO's state
	def GetOutputsState(self):
		result = []
		for slot in self.outputs:
			out_states = self.outputs[slot].get_outputs()
			for i in range(0, GPIO_board.NUM_GPIO):
				#state = self.outputs[slot].get_output(i)
				result.append( (dbus.Int16(GPIO_board.NUM_GPIO*slot + i), bool( (out_states>>i) & 0x01 ) ) )
		if (result == []): result = [-1]
		return dbus.Array( sorted(result) )



	@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='v')   # Retrieve available inputs GPIO list
	def GetInputs(self):
		result = []
		for slot in self.inputs:
			start = slot*GPIO_board.NUM_GPIO
			result += list( range(start, start + GPIO_board.NUM_GPIO) )
		if (result == []): result = [-1]
		return dbus.Array(sorted(result))

	@dbus.service.method("su.bagna.gpio", in_signature='i', out_signature='b')   # Retrieve state of the corespondent GPIO
	def GetInputState(self, num):
		return self.inputs[ num // GPIO_board.NUM_GPIO].get_input( num % GPIO_board.NUM_GPIO )

	@dbus.service.method("su.bagna.gpio", in_signature='', out_signature='v')   # Retrieve input GPIO's state
	def GetInputsState(self):
		result = dbus.Array()
		for slot in self.inputs:
			in_state = self.inputs[slot].get_inputs()
			for i in range(0, GPIO_board.NUM_GPIO):
				result.append( (dbus.Int16(GPIO_board.NUM_GPIO*slot + i), dbus.Boolean( (in_state>>i) & 0x01 )) )
		if (result == []): result = [-1]
		return dbus.Array( sorted(result) )



	@dbus.service.signal('su.bagna.gpio')
	def InputChanged(self, number, state):
		return str( [number, state] )

	@dbus.service.signal('su.bagna.gpio')
	def ShortPress(self, number):
		return str( number )

	@dbus.service.signal('su.bagna.gpio')
	def LongPress(self, number):
		return str( number )

	@dbus.service.signal('su.bagna.gpio')
	def OutputChanged(self, number, state):
		return str( [number, state] )

if __name__ == "__main__":
	Service("This is the service").run()
