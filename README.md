# SmartHouse
Smart House controlling software with pca9555 GPIO for input/output ports and DBus for comunications between hardware server part and client modules.

Base CPU Board is BeagleBone Black or Green.
Base board fot BBB is custom, main futures are - i2c expander, 1-wire provider, rs485 and CAN provider.
Also, several GPIO or 1-wire boards can be inserted to Base Board via i2c bus. All extending boards must has EEPROM to determinate type of board.

Required packages:
    apt-get install \
        python3-dbus
        python3-twisted
        python3-configobj		# for gpio_detector.py
        python3-daemon
        python3-psutil
        python3-pip
        python3-ephem		# for web ui
        python3-tzlocal		# for web ui
        python3-paho-mqtt
        python3-yaml
        apache2
        libapache2-mod-fcgid	# For FastCGI web with apache2
        mosquitto		# For mqtt support
        owserver owfs-fuse	# For 1-wire support

    pip3 install Adafruit_GPIO
    pip3 install Adafruit_BBIO
    pip3 install flup		# For fast CGI
    pip3 install pyownet	# 1-wire requires:

    scapy - For network monitoring, if needed

Configure apache2:
    dpkg-reconfigure locales
    select locale ru_RU.UTF-8
    htpasswd -c /opt/SmartHouse/passwords USER
    set name to .htaccess in /opt/SmartHouse/web/root folder

    a2enmod fcgid
    a2ensite SmartHouse.conf

    execute configure_apache2.sh
	to access web page, use http://url:80


Enable services startup:
    systemctl enable dbus_gpio.service
    systemctl enable dbus_termo.service
    systemctl enable smarthouse_clients.service
    systemctl enable smarthouse_mqtt.service
    systemctl enable smarthouse_owfs_mount.service
    systemctl enable smarthouse_owfs.service
    systemctl enable apache2
    systemctl enable mosquitto
    systemctl disable owserver


Other configurations:
    timedatectl set-timezone Europe/Minsk	# Setup timezone
    connmanctl services
    connmanctl config <service> --ipv4 manual <ip_addr> <netmask> <gateway> --nameservers <dns_server>
	Example:
	    connmanctl services		# Get services list
	    connmanctl config ethernet_78a504ca00b1_cable --ipv4 manual 192.168.1.145 255.255.255.0 192.168.1.8 --nameservers 192.168.1.8 8.8.8.8 8.8.4.4

# For upnp descovery install:
    apt-get install libgupnp-1.0-dev
    git clone https://github.com/victronenergy/simple-upnpd.git
    compile and cp simple-upnpd to /usr/local/sbin/

Links:
	Python 1wire library: https://pyownet.readthedocs.io/en/latest/protocol.html
