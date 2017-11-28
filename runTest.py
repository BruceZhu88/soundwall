#!/usr/bin/python
import unittest
import subprocess
import time
import os
import test
from lib import HTMLTestRunner

def makeDir(name):
    path = "./"+name
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def makeFile(path, name):
    now = time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
    filename = path+'/%s_'%name+now+'.html'
    fo = open(filename,"wb")
    fo.close()
    return filename

def addTest(testCase):
    testunit = unittest.TestSuite()
    for test in testCase:
	testunit.addTest(unittest.makeSuite(test))
    return testunit

def run(title, description, testunit):
    fp = file(makeFile(makeDir("report"), "test_report"), 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
    stream = fp,
    title = title,
    description = description,
    verbosity = 2)
    runner.run(testunit)
    fp.close()

if __name__ == "__main__":
    print "Running Soundwall test script version ", test.TEST_SCRIPT_VERSION
    assert subprocess.call(['pgrep', '-x', 'ModemManager']) == 1
    testCase = [
		test.GetTotalNodesTestCase,
		test.MuteModeTestCase,
                test.GetSystemInfoTestCase,
		test.GetNtcInfoTestCase,
                test.SetToneTestCase,
                test.AudioInputTestCase,
                test.FactoryResetTestCase,
                test.A2BModeTestCase,
                test.PowerModeTestCase,
		test.SetSoundModeTestCase,
		test.GetSoundModeTestCase,
                test.UpgradeMasterTestCase,
                test.UpgradeSlavesTestCase,
		]
    testunit = addTest(testCase)
    run("Soundwall Test Report","Test Execution Details:", testunit)
