# Scripts
The following script files are currently available.

* bin/setup.sh - script to setup the test environment such as udev rules and GPB.
* bin/build_dfu_util.sh - script to download and build dfu-util version 0.9
* bin/build_gpb.sh - will download the proto files from github and generate python files.
* test.py - will run some basic tests on the soundwall using the GPB.
* soundwallcmd.py - supports a number of the GPB commands of the soundwall for more information run ./soundwallcmd.py --help.
* bin/fwupdate.sh - support upgrade of the soundwall. This script will use the soundwallcmd.py.

# Setup
To run the soundwall tests you need to generate the python files from the proto files. To setup the enivornment run

* ./bin/setup.sh

Run the script and it will download the latests version of the proto-files from the github and build it using the protoc util. After this all python files will be located in the gpb directory. Make sure you have access to github. It will also try and setup some udev rules so that we get a device file /dev/soundwall

## Known Issue
It looks like Ubuntu is trying to communicate with the Soundwall as an USB modem and this can affect the communication with the Soundwall to prevent this make sure to run

sudo systemctl stop ModemManager

This will stop the service that is trying to communicate with the Soundwall many issue that we have seen might be the result of this.

# Run Tests
To run only the tests you should be able to run the ./test.py script or the ./runTest.py to generate test report. Make sure you have run the gpb/build_gpb.sh first since it will require that all the generated python files from the proto files are located in the gpb directory.

## Python Unittest
The test script is using the unittest module for more information on the module https://docs.python.org/2/library/unittest.html.

## Run A Single TestCase
Since the script is using the python unittest module to run the tests you can also run a single test case if you would like to debug it.

python -m unittest -v test.A2BModeTestCase

will run only the A2BModeTestCase and by using the -v you will get some prints when running.

# Run Single Command
If you would like to run a single command you can do so by running the script ./soundwallcmd.py for more information on what we currently support run ./soundwallcmd.py --help. This script is more or less just using the supported commands implemmented in the lib/soundwallapi.py which is what is used in the test.py script.

# Soundwall API
When adding more support for the GPB commands of the soundwall they are added to the soundwallapi.py and can then be used to extend the tests.

# Testing Upgrade
To test the upgrade of the master run the script ./dfu_master.sh all|app|btl|update. This is more or less what we are running on the Core/EZ3.
The script supports the following arguments:

* app - will only upgrade the app firmware of the master.
* btl - will only upgrade the bootloader firmware of the master.
* master - will update both the app and the bootloader firmware of the master.
* down - will downgrade the master with the firmware located in firmware/downgrade/
* slaves - will update all slaves.
* update - will only upgrade if the version located in the firmware directory is newer then what is currently running on the master.

# Testing Slave Upgrade
To test the slave upgrade run the script ./upgrade_slave.sh. It will get the number of nodes and try and upgrade them one by one. This script is using the soundwall_cmd.py script.

# Workflow
Since we are using git and this is a minor project we don't really have to have a branching stratagy but since we are on different continants it might be good to at least align it a little bit. We should create a pull request when doing any changes this is done by locally doing the following.

* git checkout master - checkout master all branches for a pull request should be based on master
* git pull - make sure you have the latest from the master locally.
* git checkout -b <name>/<branchname> - for example "git checkout -b extzig/fixing-bug-1213"
* Develop and commit you changes locally to your branch.
* git push - "git push --set-upstream origin extzig/fixing-bug-1234"

When this is done open the github and you should see a butten that create pull request extzig/fixing-bug-1213 push it and then make sure to add you reviewers.
