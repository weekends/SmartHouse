# SmartHouse
Smart House controlling software with pca9555 GPIO for input/output ports and DBus for comunications between hardware server part and client modules.

Base CPU Board is BeagleBone Black or Green.
Base board fot BBB is custom, main futures are - i2c expander, 1-wire provider, rs485 and CAN provider.
Also, several GPIO or 1-wire boards can be inserted to Base Board via i2c bus. All extending boards must has EEPROM to determinate type of board.

Required packages:
    python3-dbus
    python3-twisted
    python3-configobj   -> for gpio_detector.py
    python3-daemon
    python3-psutil
    python3-pip

    pip3 install Adafruit_GPIO
    pip3 install Adafruit_BBIO
	pip3 install flup

	1-wire requires:
	pip3 install pyownet


For FastCGI web with apache2, install:
	apt-get install libapache2-mod-fcgid

Configure apache2:
	dpkg-reconfigure locales
	select locale ru_RU.UTF-8
	htpasswd -c /opt/SmartHouse/passwords USER
	set name to .htaccess in /opt/SmartHouse/web/root folder

	a2enmod fcgid
	a2ensite SmartHouse.conf

	execute configure_apache2.sh
	to access web page, use http://url:80



