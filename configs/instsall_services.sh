#!/bin/sh

SCRIPT_DIR=$(dirname -- "$0")
DEST_SYSTEMD_PATH='/lib/systemd/system'

for f in $(ls -1 "$SCRIPT_DIR/etc/systemd/system/"); do
	cp -a "$SCRIPT_DIR/etc/systemd/system/$f" "$DEST_SYSTEMD_PATH"
	chown root.root "$DEST_SYSTEMD_PATH/$f"
	chmod 755 "$DEST_SYSTEMD_PATH/$f"
	systemctl enable $f
	systemctl restart $f
done
