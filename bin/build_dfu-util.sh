#!/bin/sh

dfu_dir=dfu-util

if [ ! -f "bin/dfu-util" ]; then
    if [ ! -d "$dfu_dir" ]; then
        echo "Downloading dfu-util...."
        git clone git://git.code.sf.net/p/dfu-util/dfu-util $dfu_dir || {
            echo "Failed to download dfu-util!"
            exit 1
        }
    fi

    echo "Install required packages..."
    sudo sed -i -- 's/#deb-src/deb-src/g' /etc/apt/sources.list && sudo sed -i -- 's/# deb-src/deb-src/g' /etc/apt/sources.list
    sudo apt-get update
    sudo apt-get build-dep dfu-util
    sudo apt-get install libusb-1.0-0-dev
fi

echo "Build dfu-util version 0.9...."
cd $dfu_dir

branch=$(git branch | grep \*)
if [ "$branch" != "* v0.9" ]; then
    git checkout tags/v0.9 -b v0.9
fi

./autogen.sh || { exit 1; }
./configure || { exit 1; }
make || { exit 1; }
cp src/dfu-util ../bin/ || { exit 1; }

