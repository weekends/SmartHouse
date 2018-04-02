# SmartHouse
Smart House controlling software with pca9555 GPIO for input/output ports and DBus for comunications between hardware server part and client modules.

Base CPU Board is BeagleBone Black or Green.
Base board fot BBB is custom, main futures are - i2c expander, 1-wire provider, rs485 and CAN provider.
Also, several GPIO or 1-wire boards can be inserted to Base Board via i2c bus. All extending boards must has EEPROM to determinate type of board.
