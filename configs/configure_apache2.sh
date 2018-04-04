#!/bin/sh

SCRIPT_DIR=$(dirname -- "$0")
DEST_SYSTEMD_PATH='/etc/apache2/sites-available/'

for f in $(ls -1 "$SCRIPT_DIR/etc/apache2/sites-available/"); do
	cp -a "$SCRIPT_DIR/etc/apache2/sites-available/$f" "$DEST_SYSTEMD_PATH"
	chown root.root "$DEST_SYSTEMD_PATH/$f"
done

a2enmod fcgid
a2ensite SmartHouse.conf

grep -q -e '^Listen 80$' /etc/apache2/ports.conf || echo 'Listen 80' >> /etc/apache2/ports.conf

systemctl restart apache2
systemctl enable apache2
