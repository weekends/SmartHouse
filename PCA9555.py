#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.Platform as Platform

OUT     = GPIO.OUT
IN      = GPIO.IN
HIGH    = GPIO.HIGH
LOW     = GPIO.LOW

RISING      = GPIO.RISING
FALLING     = GPIO.FALLING
BOTH        = GPIO.BOTH

PUD_OFF  = GPIO.PUD_OFF
PUD_DOWN = GPIO.PUD_DOWN
PUD_UP   = GPIO.PUD_UP


class PCA9555(GPIO.BaseGPIO):
	INPUT_PORT_0   = 0x00
	INPUT_PORT_1   = 0x01
	OUTPUT_PORT_0  = 0x02
	OUTPUT_PORT_1  = 0x03
	POLARITY_INV_0 = 0x04
	POLARITY_INV_1 = 0x05
	CFG_PORT_0     = 0x06
	CFG_PORT_1     = 0x07

	def __init__(self, i2c_bus, i2c_address, direction=None,i2c_interrupt_pin=None,  polarity=None, i2c=None, callback=None, **kwargs):
		self._i2c_bus = i2c_bus
		self._i2c_address = i2c_address
		self.gpios_prev = 0x0000
		self.gpios_last = 0x0000

		if i2c is None:
			import Adafruit_GPIO.I2C as I2C
			i2c = I2C
		self._device = i2c.get_i2c_device(i2c_address, busnum=i2c_bus, **kwargs)

		if ((direction == None) or (direction == OUT)):
			self.setup_pins_out()
			self.i2c_interrupt_pin = None
			self._callback = None
		else:
			self.i2c_interrupt_pin = i2c_interrupt_pin
			self.polarity = polarity
			if (self.i2c_interrupt_pin == None):
				print("No interrupt pin defined, work without interrupts")
			self._callback = callback
			self.setup_pins_in()
			self.read_gpios()

	def setup_pins(self, pins):
		"""Setup multiple pins as inputs or outputs at once.  Pins should be a
		dict of pin name to pin type (IN or OUT).
		"""
		pins = 0x0000
		# General implementation that can be optimized by derived classes.
		for pin, value in iter(pins.items()):
			if (value == IN):
				res += (1<<pin)
			#self.setup(pin, value)
		self._device.write8(self.CFG_PORT_0, (pins & 0xFF) )
		self._device.write8(self.CFG_PORT_1, ((pins>>8) & 0xFF) )

	def setup_pins_out(self, value = 0x0000):
		""" Init all pins as Outputs """
		self._device.write8(self.CFG_PORT_0, 0x00)
		self._device.write8(self.CFG_PORT_1, 0x00)
		self.set_outputs(value)

	def setup_pins_in(self):
		""" Init all pins as Inputs """
		self._device.write8(self.CFG_PORT_0, 0xFF)
		self._device.write8(self.CFG_PORT_1, 0xFF)
		if (self.polarity != None):
			self._device.write8(self.POLARITY_INV_0, 0xFF)
			self._device.write8(self.POLARITY_INV_1, 0xFF)
		else:
			self._device.write8(self.POLARITY_INV_0, 0x00)
			self._device.write8(self.POLARITY_INV_1, 0x00)

		if (self.i2c_interrupt_pin != None):
			gpio_ints = GPIO.get_platform_gpio()
			gpio_ints.setup(self.i2c_interrupt_pin, IN, PUD_UP)
			gpio_ints.add_event_detect(self.i2c_interrupt_pin, FALLING, callback=self.read_gpios_callback, bouncetime=-1)

	def read_gpios(self):
		self.gpios_last = self._device.readU8(self.INPUT_PORT_0) + (self._device.readU8(self.INPUT_PORT_1)<<8)

	def read_gpios_callback(self, pin):
		self.read_gpios()
		if (self.gpios_prev != self.gpios_last):
			if (self._callback != None): self._callback(self.gpios_prev, self.gpios_last, pin)
			self.gpios_prev = self.gpios_last


	def set_outputs(self, value):
		self._device.write8(self.OUTPUT_PORT_0, (value & 0xFF))
		self._device.write8(self.OUTPUT_PORT_1, (value>>8 & 0xFF))


	def output(self, pin, value):
		"""Set the specified pin the provided high/low value.  Value should be
		either HIGH/LOW or a boolean (true = high)."""
		if ((pin >= 0) and (pin < 8)):
			port = self.OUTPUT_PORT_0
		elif ((pin >= 8 ) and (pin < 16)):
			port = self.OUTPUT_PORT_1
			pin -= 8
		else:
			print("Port: %d out of range 0..15" % pin)
			raise OverflowError

		current_state = self._device.readU8(port)
		current_state = (current_state | 1<<pin) if ((value == HIGH) or (value == True)) else (current_state & ~(1<<pin))
		self._device.write8(port, current_state)

	def input(self, pin):
		"""Read the specified pin and return HIGH/true if the pin is pulled high,
		or LOW/false if pulled low."""
		res = False
		if ((pin >= 0) and (pin < 16)):
			res = ( (self.gpios_last & 1<<pin) == 1<<pin )
		else:
			print("Port: %d out of range 0..15" % pin)
		return res

	def get_output(self, pin):
		pins = self.get_outputs()
		if ((pin >= 0) and (pin < 16)):
			return (pins & (1<<pin)) == (1<<pin)
		else:
			print("Port: %d out of range 0..15" % pin)
		return False

	def get_outputs(self):
		return self._device.readU8(self.OUTPUT_PORT_0) + (self._device.readU8(self.OUTPUT_PORT_1)<<8)

	def get_inputs(self):
		if (self.i2c_interrupt_pin == None):
			self.read_gpios()
		return self.gpios_last
