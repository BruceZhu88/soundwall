#!/bin/sh
DFU_BIN_DIR=$(pwd)/bin
SOUNDWALL_DFU_UTIL_ERRORS=/tmp/dfu-util-errors
SOUNDWALL_BTL_IMAGE_PREFIX=firmware/upgrade/beo-ase2-soundwall-bl_
SOUNDWALL_APP_IMAGE_PREFIX=firmware/upgrade/beo-ase2-soundwall-app_
SOUNDWALL_BTL_IMAGE=$(echo $SOUNDWALL_BTL_IMAGE_PREFIX*.bin | awk '{print $1}')
SOUNDWALL_BTL_IMAGE_VERSION=$(echo $SOUNDWALL_BTL_IMAGE | awk '{split($0,tmp,".bin")}{n=split(tmp[1], array,"_")} END{print array[n]}')
SOUNDWALL_APP_IMAGE=$(echo $SOUNDWALL_APP_IMAGE_PREFIX*.bin | awk '{print $1}')
SOUNDWALL_APP_IMAGE_VERSION=$(echo $SOUNDWALL_APP_IMAGE | awk '{split($0,tmp,".bin")}{n=split(tmp[1], array,"_")} END{print array[n]}')
SOUNDWALL_BTL_ADDRESS=0x08000000
SOUNDWALL_APP_ADDRESS=0x08004000
SOUNDWALL_DEVICE=/dev/soundwall
SOUNDWALL_VID=0483
SOUNDWALL_APP_PID=5740
SOUNDWALL_DFU_PID=df11
SOUNDWALL_MAX_NBR_OF_TRIES=10
SOUNDWALL_CURRENT_APP_VERSION=""
SOUNDWALL_CURRENT_BTL_VERSION=""
SOUNDWALL_UPDATE_APP="YES"
SOUNDWALL_UPDATE_BTL="YES"
SOUNDWALL_UPDATE_SLAVES="NO"
SOUNDWALL_MODE="APP"
SOUNDWALL_ARG=$1
alias soundwall_cli=$(pwd)/soundwallcmd.py

soundwall_wait_for_dev()
{
	local counter=0
	while true; do
		if [ -h "$SOUNDWALL_DEVICE" ]; then
			echo "SOUNDWALL update: Device ready"
			return 0;
		fi

		sleep 1

		if [ "$counter" -eq "$SOUNDWALL_MAX_NBR_OF_TRIES" ]; then
			return 1;
		fi
		counter=$((counter+1))
	done
}

soundwall_wait_for_app()
{
	local counter=0
	while true; do
		lsusb -d $SOUNDWALL_VID:$SOUNDWALL_APP_PID > /dev/null && {
			echo "SOUNDWALL update: App running"
			return 0;
		}

		sleep 1

		if [ "$counter" -eq "$SOUNDWALL_MAX_NBR_OF_TRIES" ]; then
			return 1;
		fi
		counter=$((counter+1))
	done
}

soundwall_wait_for_master()
{
	soundwall_wait_for_app || {
		echo 1>&2 "SOUNDWALL update: soundwall APP not running!"
		return 1
	}

	soundwall_wait_for_dev || {
		echo 1>&2 "SOUNDWALL update: soundwall device not ready!"
		return 1
	}

	return 0
}

soundwall_system_restart()
{
	soundwall_cli --system-restart || {
		echo 1>&2 "SOUNDWALL update: failed to restart soundwall!"
		return 1
	}

	sleep 2

	soundwall_wait_for_master || return 1

	return 0
}

# wait for the soundwall to enter dfu mode
soundwall_wait_for_dfu()
{
	local counter=0
	while true; do
		lsusb -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID > /dev/null && {
			echo "SOUNDWALL update: entered dfu"
			return 0;
		}

		sleep 1

		if [ "$counter" -eq "$SOUNDWALL_MAX_NBR_OF_TRIES" ]; then
			return 1;
		fi
		counter=$((counter+1))
	done
}

soundwall_check_mode()
{
	SOUNDWALL_MODE="APP"
	lsusb -d $SOUNDWALL_VID:$SOUNDWALL_APP_PID > /dev/null && return 0

	SOUNDWALL_MODE="DFU"
	lsusb -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID > /dev/null || {
		SOUNDWALL_MODE="NA"
		echo 1>&2 "SOUNDWALL update: missing Soundwall device!"
		return 1
	}

	return 0
}

soundwall_run_dfu()
{
	# when running the dfu-util on the ASE platform with the DfuSe command leave we
	# get the error code -4 which is comming from the libusb because the device
	# is not available anymore probably because the device have already left the dfu
	# mode. Not sure why this only happens on the ASE platform when running on the PC
	# we cannot reproduce it. So this is why we ignores the return value when issue
	# leave command. For more information https://github.com/spark/firmware/issues/599.
	if [ "$SOUNDWALL_UPDATE_BTL" == "YES" ] && [ "$SOUNDWALL_UPDATE_APP" == "YES" ]; then
		echo "SOUNDWALL update: upgrade BTL to version=$SOUNDWALL_BTL_IMAGE_VERSION"
		$DFU_BIN_DIR/dfu-util -a 0 -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID -s $SOUNDWALL_BTL_ADDRESS -D $SOUNDWALL_BTL_IMAGE || {
			echo 1>&2 "SOUNDWALL update: Update BTL failed!"
			return 1
		}

		echo "SOUNDWALL update: upgrade APP to version=$SOUNDWALL_APP_IMAGE_VERSION"
		$DFU_BIN_DIR/dfu-util -a 0 -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID -s $SOUNDWALL_APP_ADDRESS:leave -D $SOUNDWALL_APP_IMAGE 2> $SOUNDWALL_DFU_UTIL_ERRORS

	elif [ "$SOUNDWALL_UPDATE_BTL" == "YES" ] && [ "$SOUNDWALL_UPDATE_APP" == "NO" ]; then
		echo "SOUNDWALL update: upgrade BTL to version=$SOUNDWALL_BTL_IMAGE_VERSION"
		$DFU_BIN_DIR/dfu-util -a 0 -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID -s $SOUNDWALL_BTL_ADDRESS:leave -D $SOUNDWALL_BTL_IMAGE 2> $SOUNDWALL_DFU_UTIL_ERRORS

	elif [ "$SOUNDWALL_UPDATE_BTL" == "NO" ] && [ "$SOUNDWALL_UPDATE_APP" == "YES" ]; then
		echo "SOUNDWALL update: upgrade APP to version=$SOUNDWALL_APP_IMAGE_VERSION"
		$DFU_BIN_DIR/dfu-util -a 0 -d $SOUNDWALL_VID:$SOUNDWALL_DFU_PID -s $SOUNDWALL_APP_ADDRESS:leave -D $SOUNDWALL_APP_IMAGE 2> $SOUNDWALL_DFU_UTIL_ERRORS
	fi

	return 0
}

soundwall_dfu()
{
	if [ ! -f "$SOUNDWALL_APP_IMAGE" ]; then
		echo 1>&2 "SOUNDWALL update: unable to read APP firmware!"
		return 1
	fi

	if [ ! -f "$SOUNDWALL_BTL_IMAGE" ]; then
		echo 1>&2 "SOUNDWALL update: unable to read BTL firmware!"
		return 1
	fi
	
	soundwall_check_mode || return 1

	if [ "$SOUNDWALL_MODE" != "DFU" ]; then
		echo 1>&2 "SOUNDWALL update: not in DFU mode!"
		return 1
	fi

	soundwall_run_dfu || return 1

	soundwall_wait_for_master || return 1

	return 0
}

soundwall_enter_dfu_mode()
{
	soundwall_check_mode || return 1
	
	if [ "$SOUNDWALL_MODE" == "DFU" ]; then
		echo "SOUNDWALL update: already in DFU mode!" 
		return 0
	fi
	
	# switch to bootloader DFU mode
	soundwall_cli --enter-dfu > /dev/null || {
		echo 1>&2 "SOUNDWALL update: failed to enter dfu!"
		return 1
	}
		
	soundwall_wait_for_dfu || {
		echo 1>&2 "SOUNDWALL update: soundwall failed to enter DFU!"
		return 1
	}

	return 0
}

soundwall_wake_up()
{
	soundwall_check_mode || return 1
	
	# We should only wake it up if the soundwall is in APP mode
	if [ "$SOUNDWALL_MODE" == "APP" ]; then
		soundwall_cli --set-power-mode working > /dev/null || {
			echo 1>&2 "SOUNDWALL update: failed to wakeup Soundwall when in standby!"
			return 1
		}
	fi

	return 0
}

soundwall_check_version()
{
	soundwall_wake_up || return 1

	version=$(soundwall_cli --system-info 0 | grep -A 1 APP | head -2 | grep version | awk '{ print $2 }')
	version=${version%*\"}
	SOUNDWALL_CURRENT_APP_VERSION=${version#\"*}
	if [ -z "$SOUNDWALL_CURRENT_APP_VERSION" ]; then
		echo 1>&2 "SOUNDWALL update: Unable to read soundwall APP version!"
		return 1
	fi
	
	version=$(soundwall_cli --system-info 0 | grep -A 1 BTL | head -2 | grep version | awk '{ print $2 }')
	version=${version%*\"}
	SOUNDWALL_CURRENT_BTL_VERSION=${version#\"*}
	if [ -z "$SOUNDWALL_CURRENT_BTL_VERSION" ]; then
		echo 1>&2 "SOUNDWALL update: Unable to read soundwall BTL version!"
		return 1
	fi

	return 0
}

soundwall_verify_update()
{
	soundwall_check_version || return 1

	if [ "$SOUNDWALL_APP_IMAGE_VERSION" == "$SOUNDWALL_CURRENT_APP_VERSION" ] && [ "$SOUNDWALL_BTL_IMAGE_VERSION" == "$SOUNDWALL_CURRENT_BTL_VERSION" ]; then
		# Successful soundwall update
		echo "SOUNDWALL update: Update done."
		return 0
	fi

	echo "SOUNDWALL update: Update failed."
	return 1
}

soundwall_check_for_old_firmware()
{
	# If already in DFU mode we can continue
	# our normal procedure
	soundwall_check_mode || return 1
	if [ "$SOUNDWALL_MODE" == "DFU" ]; then
		return 0
	fi
	# If we can wake the soundwall from
	# standby then it is not old firmware
	soundwall_wake_up && return 0
	# If we can get the version it is not old firmware
	soundwall_check_version && return 0
	soundwall_enter_dfu_mode || {
		# If it didn't work there are two other possible sequences 
		# that can set the old firmware in DFU.
		stty -F $SOUNDWALL_DEVICE speed 115200 cs8 -cstopb -parenb -echo
		# Sequence 1
		echo -en '\x7E\xFF\x10\x0A\x04\x08\x22\x48\x00\x70\x1B\x7E' > $SOUNDWALL_DEVICE
		# Sequence 2
		echo -en '\x7E\xFF\x10\x0A\x05\x08\xCF\x01\x48\x00\x04\xAA\x7E' > $SOUNDWALL_DEVICE
		# Give the soundwall some time to enter DFU
		sleep 1
		# Let's check for some DFU device
		soundwall_check_mode || return 1
		if [ "$SOUNDWALL_MODE" != "DFU" ]; then
			echo 1>&2 "SOUNDWALL update: looks like some old firmware is currently running and we fail to set it in DFU!"
			return 1
		fi
	}

	return 0
}

soundwall_update_slaves()
{
	 # Skip this if we are in DFU mode
	soundwall_check_mode || return 1
	if [ "$SOUNDWALL_MODE" == "DFU" ]; then
		return 0
	fi

	# We should always start the upgrade with the slave node at end
	# and end with slave node one
	flag=$(soundwall_cli --get-a2b-dfu-flag | grep dfu)

	if [ "$flag" == "dfu" ]; then
		echo 1>&2 "SOUNDWALL update: one slave node was in A2B DFU mode let's upgrade all slaves!"
		SOUNDWALL_UPDATE_SLAVES=YES
		# We need this restart because of SWL-74
		soundwall_system_restart || {
			echo 1>&2 "SOUNDWALL update: soundwall failed to restart system!"
			return 1
		}
	fi

	if [ "$SOUNDWALL_UPDATE_SLAVES" == "YES" ]; then
		soundwall_cli --upgrade-all-slaves || return 1
	fi

	return 0
}

soundwall_update()
{
	soundwall_enter_dfu_mode || return 1
	soundwall_dfu || return 1
	soundwall_verify_update || {
		# If we fail to verify the installation we should dump the dfu-util errors
		if [ -e "$SOUNDWALL_DFU_UTIL_ERRORS" ]; then
			echo 1>&2 "SOUNDWALL update: =======dfu-util errors======="
			cat $SOUNDWALL_DFU_UTIL_ERRORS
			echo 1>&2 "SOUNDWALL update: ============================="
		fi
		return 1
	}

	soundwall_update_slaves || return 1
}

soundwall_update_if_needed()
{
	if [ "$SOUNDWALL_MODE" == "APP" ]; then
		echo "SOUNDWALL update: application running!"

		soundwall_check_version || return 1

		echo "SOUNDWALL update: current APP version=$SOUNDWALL_CURRENT_APP_VERSION"
		echo "SOUNDWALL update: current BTL version=$SOUNDWALL_CURRENT_BTL_VERSION"

		SOUNDWALL_UPDATE_APP="YES"
		if [ "$SOUNDWALL_APP_IMAGE_VERSION" == "$SOUNDWALL_CURRENT_APP_VERSION" ]; then
			SOUNDWALL_UPDATE_APP="NO"
		fi

		SOUNDWALL_UPDATE_BTL="YES"
		if [ "$SOUNDWALL_BTL_IMAGE_VERSION" == "$SOUNDWALL_CURRENT_BTL_VERSION" ]; then
			SOUNDWALL_UPDATE_BTL="NO"
		fi

		if [ "$SOUNDWALL_UPDATE_APP" == "NO" ] && [ "$SOUNDWALL_UPDATE_BTL" == "NO" ]; then
			echo "SOUNDWALL update: Update is not necessary"
			SOUNDWALL_UPDATE_SLAVES="NO"
			# Test and see if any slaves are in A2B DFU mode and if so upgrade them all
			soundwall_update_slaves || return 1
			return 0
		fi
	fi

	soundwall_update || return 1
}

# If old firmware we will not be able to communicate with the tile
# and we need to force it in DFU and then upgrade the firmware.
# This is something that will only occure during training since
# the initial HW did not contain working firmware.
# This should be removed in the future.
soundwall_check_for_old_firmware || exit 1

# we need to make sure that the soundwall is not in standby
soundwall_wake_up || exit 1

if [ "$SOUNDWALL_ARG" == "master" ]; then
	SOUNDWALL_UPDATE_BTL="YES"
	SOUNDWALL_UPDATE_APP="YES"
	SOUNDWALL_UPDATE_SLAVES="NO"
	soundwall_update || exit 1
elif [ "$SOUNDWALL_ARG" == "btl" ]; then
	SOUNDWALL_UPDATE_BTL="YES"
	SOUNDWALL_UPDATE_APP="NO"
	soundwall_update || exit 1
elif [ "$SOUNDWALL_ARG" == "app" ]; then
	SOUNDWALL_UPDATE_BTL="NO"
	SOUNDWALL_UPDATE_APP="YES"
	soundwall_update || exit 1
elif [ "$SOUNDWALL_ARG" == "down" ]; then
	SOUNDWALL_BTL_IMAGE_PREFIX=firmware/downgrade/beo-ase2-soundwall-bl_
	SOUNDWALL_APP_IMAGE_PREFIX=firmware/downgrade/beo-ase2-soundwall-app_
	SOUNDWALL_BTL_IMAGE=$(echo $SOUNDWALL_BTL_IMAGE_PREFIX*.bin | awk '{print $1}')
	SOUNDWALL_BTL_IMAGE_VERSION=$(echo $SOUNDWALL_BTL_IMAGE | awk '{split($0,tmp,".bin")}{n=split(tmp[1], array,"_")} END{print array[n]}')
	SOUNDWALL_APP_IMAGE=$(echo $SOUNDWALL_APP_IMAGE_PREFIX*.bin | awk '{print $1}')
	SOUNDWALL_APP_IMAGE_VERSION=$(echo $SOUNDWALL_APP_IMAGE | awk '{split($0,tmp,".bin")}{n=split(tmp[1], array,"_")} END{print array[n]}')
	soundwall_update || exit 1
elif [ "$SOUNDWALL_ARG" == "slaves" ]; then
	SOUNDWALL_UPDATE_BTL="NO"
	SOUNDWALL_UPDATE_APP="NO"
	SOUNDWALL_UPDATE_SLAVES="YES"
	soundwall_cli --upgrade-all-slaves || exit 1
elif [ "$SOUNDWALL_ARG" == "update" ]; then
	SOUNDWALL_UPDATE_SLAVES="YES"
	soundwall_update_if_needed || exit 1
else
	echo 1>&2 "SOUNDWALL update: unsupported args $SOUNDWALL_ARG!"
	exit 1
fi

exit 0
