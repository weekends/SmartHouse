#!/usr/bin/env python3
#coding=utf-8
#-*- coding: utf-8 -*-

import glob
import os.path
import struct

SH_UNKNOWN  = 0
SH_BASE		= 1
SH_GPIO_IN	= 2
SH_GPIO_OUT	= 3
SH_1WIRE	= 4

SH_BASE_PNSTR		= "SH-Base"
SH_GPIO_IN_PNSTR	= "SH-Input"
SH_GPIO_OUT_PNSTR	= "SH-Output"
SH_1WIRE_PNSTR		= "SH-1wire"

MAGIC_STR = b'\xaaU3\xee'

#typedef struct _eeprom_t
#{
#  unsigned char   magic[4];
#  unsigned char   rev[2];
#  unsigned char   bname[32];
#  unsigned char   version[4];
#  unsigned char   manufacturer[16];
#  unsigned char   part_number[16];
#  unsigned char   n_pins[2];
#  unsigned char   serial[12];
#  unsigned char   pin[148];
#  unsigned char   vdd_3v3[2];
#  unsigned char   vdd_5v[2];
#  unsigned char   sys_5v[2];
#  unsigned char   dc[2];
#} EEPROM_HDR;
struct_fmt = '=4s2s32s4s16s16s2s12s148s2s2s2s2s'
struct_len = struct.calcsize(struct_fmt)
struct_unpack = struct.Struct(struct_fmt).unpack_from

class Cape(object):
	Slot = 0
	Type = SH_UNKNOWN
	eeprom_file = ""
	eeprom_i2c_address = 0x20
	i2c_bus = 1
	gpio_i2c_address_int = []

	def __init__(self, eeprom_file, i2c_bus, i2c_address):
		self.set_eeprom_file(eeprom_file)
		self.set_i2c_bus(i2c_bus)
		self.set_eeprom_i2c_address(i2c_address)

	def set_slot(self, data): self.Slot = data
	def set_type(self, data): self.Type = data
	def set_eeprom_file(self, data): self.eeprom_file = data
	def set_eeprom_i2c_address(self, data): self.eeprom_i2c_address = data
	def set_i2c_bus(self, data): self.i2c_bus = data
	def set_gpio_i2c_address(self, data): self.gpio_i2c_address = data
	def add_gpio_i2c_address(self, data): self.gpio_i2c_address.append(data)
	def get_slot(self): return self.Slot
	def get_type(self): return self.Type
	def get_eeprom_file(self): return self.eeprom_file
	def get_eeprom_i2c_address(self): return self.eeprom_i2c_address
	def get_i2c_bus(self): return self.i2c_bus
	def get_gpio_i2c_address(self): return self.gpio_i2c_address

class EEPROM(object):
	data = []
	def __init__(self, sysfs_driver_dir='/sys/bus/i2c/drivers/at24', sysfs_eeprom_file='eeprom'):
		self.sysfs_driver_dir=sysfs_driver_dir
		for i2c_eeprom_path in sorted(glob.iglob(self.sysfs_driver_dir + '/[0-9]*')):
			eeprom_file = i2c_eeprom_path + "/" + sysfs_eeprom_file
			(fdir, fname) = os.path.split(i2c_eeprom_path)
			(i2c_bus_str, i2c_address_str) = fname.split('-')
			i2c_bus = int(i2c_bus_str)
			i2c_address = int(i2c_address_str, 16)
			self.data.append( Cape(eeprom_file, i2c_bus, i2c_address) )

	def get_files(self):
		res = []
		for f in self.data:
			res.append( f.get_eeprom_file() )
		return res

	def get_data(self): return self.data
	def remove(self, data): self.data.remove(data)


class CapeDetector(object):
	capes=[]

	gpio_cape_addresses = [
		[1, 2, 0x54, 0x20, 0x21, "P8_43", "P8_44"],	# Cape 1, i2c Bus 2, EEaddr: 0x54, pca9555: 0x20, 0x21, Int: P8_43, P8_44
		[2, 2, 0x55, 0x22, 0x23, "P8_41", "P8_42"],	# Cape 2, i2c Bus 2, EEaddr: 0x55, pca9555: 0x22, 0x23, Int: P8_41, P8_42
		[3, 2, 0x56, 0x24, 0x25, "P8_39", "P8_40"],	# Cape 3, i2c Bus 2, EEaddr: 0x56, pca9555: 0x24, 0x25, Int: P8_39, P8_40
		[4, 2, 0x57, 0x26, 0x27, "P8_34", "P8_36"],	# Cape 4, i2c Bus 2, EEaddr: 0x57, pca9555: 0x26, 0x27, Int: P8_34, P8_36
		[5, 1, 0x54, 0x20, 0x21, "P8_31", "P8_32"],	# Cape 5, i2c Bus 1, EEaddr: 0x54, pca9555: 0x20, 0x21, Int: P8_31, P8_32
		[6, 1, 0x55, 0x22, 0x23, "P8_29", "P8_30"],	# Cape 6, i2c Bus 1, EEaddr: 0x55, pca9555: 0x22, 0x23, Int: P8_29, P8_30
		[7, 1, 0x56, 0x24, 0x25, "P8_27", "P8_28"],	# Cape 7, i2c Bus 1, EEaddr: 0x56, pca9555: 0x24, 0x25, Int: P8_27, P8_28
		[8, 1, 0x57, 0x26, 0x27, "P8_19", "P8_26"]	# Cape 8, i2c Bus 1, EEaddr: 0x57, pca9555: 0x26, 0x27, Int: P8_19, P8_26
	]

	def __init__(self):
		eeprom = EEPROM()
		for eeprom_info in eeprom.get_data():
			i2c_bus = eeprom_info.get_i2c_bus()
			eeprom_i2c_address = eeprom_info.get_eeprom_i2c_address()
			eeprom_data = []

			try:
				with open(eeprom_info.get_eeprom_file(), "rb") as f:
					data = f.read(struct_len)
					if not data:
						print("There are no data in eeprom: Bus:%d Addr:0x%02X" % (i2c_bus, eeprom_i2c_address) )
						continue
					eeprom_data = struct_unpack(data)
			except:
				print("Slot Bus:%d Addr:0x%02X empty or EEProm errors..." % (i2c_bus, eeprom_i2c_address) )
				#eeprom.remove(eeprom_info)
				continue

			if (eeprom_data[0] == MAGIC_STR):
				rev          = eeprom_data[1].decode("utf-8").rstrip('\x00').rstrip('\\xff')
				bname        = eeprom_data[2].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')
				version      = eeprom_data[3].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')
				manufacturer = eeprom_data[4].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')
				part_number  = eeprom_data[5].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')
				n_pins       = eeprom_data[6].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')
				serial       = eeprom_data[7].decode("utf-8", 'backslashreplace').rstrip('\x00').rstrip('\\xff')

				if   (part_number == SH_BASE_PNSTR):	board_type = SH_BASE
				elif (part_number == SH_GPIO_IN_PNSTR):	board_type = SH_GPIO_IN
				elif (part_number == SH_GPIO_OUT_PNSTR):board_type = SH_GPIO_OUT
				elif (part_number == SH_1WIRE_PNSTR):	board_type = SH_1WIRE
				else: board_type = SH_UNKNOWN

				slot = 0
				gpios = []
				for l in self.gpio_cape_addresses:
					if ((i2c_bus == l[1]) and (eeprom_i2c_address == l[2])):
						slot = l[0]
						if ((board_type == SH_GPIO_IN) or (board_type == SH_GPIO_OUT)):
							gpios = [ [l[3],l[5]], [l[4],l[6]] ]
							break
				eeprom_info.set_slot(slot)
				eeprom_info.set_type(board_type)
				eeprom_info.set_gpio_i2c_address(gpios)
				self.capes.append(eeprom_info)
			else:
				print("Incorrect magic (%s) in eeprom: Bus:%d Addr:0x%02X" % (eeprom_data[0], i2c_bus, eeprom_i2c_address) )


	def get(self): return self.capes

	def get_type(self, t):
		res = []
		for cape in self.capes:
			if cape.get_type() == t:
				res.append(cape)
		return res

	def get_inputs(self): return self.get_type(SH_GPIO_IN)
	def get_outputs(self): return self.get_type(SH_GPIO_OUT)
	def get_1wire(self): return self.get_type(SH_1WIRE)

	def get_slot_by_interrupt_pin(self, int_pin):
		for cape in self.gpio_cape_addresses:
			if (int_pin == cape[5]): return [cape[0], 0]
			elif (int_pin == cape[6]): return [cape[0], 1]
		return []



class GPIOmapper(object):
	def __init__(self, gpio=0, pin=None, slot=None, bank=None):
		if (gpio != None):
			self._gpio = gpio
			[self._pin, self._slot, self._bank] = self.getSlot()
		elif ((pin != None) and (slot != None) and (bank != None)):
			self._pin = pin
			self._slot = slot
			self._bank = bank
			self._gpio = self.getGPIO()

	@classmethod
	def Slot(cls, pin, slot, bank): return cls(gpio=None, pin=pin, slot=slot, bank=bank)

	@classmethod
	def GPIO(cls, gpio): return cls(gpio = gpio)

	def getGPIO(self): return self._pin + self._slot*32 + self._bank*16

	def getSlot(self):
		pin = self._gpio
		slot = pin // 32
		pin -= slot*32
		if (pin > 15):
			pin -= 16
			bank = 1
		else:
			bank = 0
		return [pin, slot, bank]

	def get_gpio(self): return self._gpio
	def get_pin(self): return self._pin
	def get_slot(self): return self._slot
	def get_bank(self): return self._bank
	def get_psb(self): return [self._pin, self._slot, self._bank]


if __name__ == "__main__":
	capes = CapeDetector()

	print("All founded capes:")
	for cape in capes.get():
		print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )

	print("\nInputs:")
	for cape in capes.get_inputs():
		print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )

	print("\nOutputs:")
	for cape in capes.get_outputs():
		print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )

	print("\n1-wire:")
	for cape in capes.get_1wire():
		print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )

	print("\nInputs and Outputs:")
	for cape in capes.get_inputs() + capes.get_outputs():
		print(cape.get_slot(), cape.get_type(), cape.get_gpio_i2c_address() )
