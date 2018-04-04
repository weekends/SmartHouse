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

For FastCGI web with apache2, install:
	apt-get install libapache2-mod-fcgid

Configure apache2:
	a2enmod fcgid

	/etc/apache2/ports.conf
	Change Listen 8080 to needed port, default must be 80
		Listen 8080 -> Listen 80


	/etc/apache2/sites-enabled/000-default.conf
	Add after <VirtualHost *:80>

		DocumentRoot /opt/SmartHouse/web/root
		<Directory />
			Options FollowSymLinks
			AllowOverride all
			Allow from all
			Require all granted
		</Directory>

		<Directory "/opt/SmartHouse/web/root/cgi-bin">
			AllowOverride None
			Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
			Require all granted
		</Directory>

		ScriptAlias /cgi-bin/ /opt/SmartHouse/web/root/cgi-bin/
		<Directory /opt/SmartHouse/web/root>
			Options +ExecCGI
			DirectoryIndex index.html
		</Directory>
		AddHandler cgi-script .cgi

	comment line: DocumentRoot /var/www/html
	DocumentRoot /var/www/html	-> #   DocumentRoot /var/www/html

