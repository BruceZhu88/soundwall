#!/bin/bash

LOCAL_BIN_DIR=$(pwd)/bin
UDEV_SOUNDWALL_RULES=10-soundwall.rules

./bin/build_gpb.sh || {
    echo "ERROR: failed to setup gpb"
    exit 1
}

./bin/build_dfu-util.sh || {
    echo "ERROR: failed to build dfu-util"
    exit 1
}

if [ ! -f "$UDEV_SOUNDWALL_RULS" ]; then
    touch $UDEV_SOUNDWALL_RULES
fi

echo "SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"0483\", ATTRS{idProduct}==\"5740\", SYMLINK+=\"soundwall\"" > $UDEV_SOUNDWALL_RULES

sudo mv $UDEV_SOUNDWALL_RULES /etc/udev/rules.d/ || {
    echo "ERROR: failed to copy udev rules"
    exit 1
}

sudo udevadm control --reload-rules  || {
    echo "ERROR: failed to reload rules"
    exit 1
}

sudo udevadm trigger || {
    echo "ERROR: failed to trigger rules"
    exit 1
}

sudo systemctl stop ModemManager || {
    echo "ERROR: failed to stop ModemManager, this might affect the test result!"
    exit 1
}
