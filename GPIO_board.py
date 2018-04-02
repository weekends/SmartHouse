#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PCA9555 as GPIO
from PCA9555 import PCA9555 as PCA9555
import Adafruit_GPIO.I2C as I2C

class GPIO_board(object):
	NUM_GPIO = 32

	def __init__(self, i2c_bus, i2c_addr, direction=None, i2c_interrupt_pins=None,  polarity=None, i2c=I2C, callback=None, slot=None, **kwargs):
		self._slot = slot
		if (direction == GPIO.OUT):
			self._gpios = { 0:PCA9555(i2c_bus, i2c_addr[0], GPIO.OUT, i2c),
							1:PCA9555(i2c_bus, i2c_addr[1], GPIO.OUT, i2c) }
		else:
			self.callback = callback
			self.i2c_interrupt_pins = i2c_interrupt_pins
			self._gpios = { 0:PCA9555(i2c_bus, i2c_addr[0], GPIO.IN, i2c_interrupt_pins[0], polarity, i2c, self._callback),
							1:PCA9555(i2c_bus, i2c_addr[1], GPIO.IN, i2c_interrupt_pins[1], polarity, i2c, self._callback) }
			self._gpios_prev = {0:0x0000, 1:0x0000}
			self._gpios_last = {0:0x0000, 1:0x0000}

	def get_pin_controller(self, pin):
		PCA9555._validate_pin(self, pin)
		bank = 0 if (pin < self.NUM_GPIO//2) else 1
		return [pin - bank*(self.NUM_GPIO//2), self._gpios.get(bank)]

	def set_pin(self, pin, value):
		PCA9555._validate_pin(self, pin)
		#print("Set pin: %2d to value: %d" % (pin, value))
		[norm_pin, gpio] = self.get_pin_controller(pin)
		gpio.output(norm_pin, value)
		return True

	def set_pins(self, values):
		self._gpios.get(0).set_outputs(values & 0xFFFF)
		self._gpios.get(1).set_outputs((values>>16) & 0xFFFF)

	def get_output(self, pin):
		PCA9555._validate_pin(self, pin)
		bank = 0 if (pin < self.NUM_GPIO//2) else 1
		return self._gpios[bank].get_output(pin - bank*(self.NUM_GPIO//2) )

	def get_input(self, pin):
		PCA9555._validate_pin(self, pin)
		bank = 0 if (pin < self.NUM_GPIO//2) else 1
		return self._gpios[bank].input(pin - bank*(self.NUM_GPIO//2) )


	def get_outputs(self):
		return self._gpios[0].get_outputs() + (self._gpios[1].get_outputs() <<  (self.NUM_GPIO//2) )

	def get_inputs(self):
		return self._gpios[0].get_inputs() + (self._gpios[1].get_inputs() <<  (self.NUM_GPIO//2) )

	def _callback(self, prev, last, interrupt):
		bank = 0 if (self.i2c_interrupt_pins[0] == interrupt) else 1
		self._gpios_prev[bank] = prev
		self._gpios_last[bank] = last
		self.callback( self._gpios_prev.get(0)+(self._gpios_prev.get(1)<<16), self._gpios_last.get(0)+(self._gpios_last.get(1)<<16), self._slot )
		self._gpios_prev[bank] = self._gpios_last[bank]

if __name__ == "__main__":
	import time
	gpio_out = GPIO_board( i2c_bus=2, i2c_addr=[0x20, 0x21], direction=GPIO.OUT)

	def test_callback(prev, cur):
		print("Called: 0x%08X -> 0x%08X" % (prev, cur) )

	gpio_in = GPIO_board( i2c_bus=1, i2c_addr=[0x24, 0x25], direction=GPIO.IN, i2c_interrupt_pins=['P8_27', 'P8_28'], polarity=True, callback=test_callback)

	while True:
		for i in range(0, gpio_out.NUM_GPIO):
			#gpio_out.set_pin(i, 1)
			#gpio_out.set_pins(1<<i)
			gpio_out.set_pins(0xFFFF0000)
			time.sleep(0.5)
			gpio_out.set_pins(0x0000FFFF)
			time.sleep(0.5)
			#gpio_out.set_pin(i, 0)
