#!/usr/bin/python
import unittest
import subprocess
import time
from lib import soundwallapi
from lib import EqData
from gpb import soundwall_pb2
from gpb import dsp_pb2
class CmdStressTestCase(unittest.TestCase):
    def setUp(self):
        self.api = soundwallapi.SoundwallApi()
    def tearDown(self):
        self.api.close()
    def testMasterGetTotalNodes(self):
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	print "totalNodes=",totalNodes
    def testMasterGetSystemVersionInfo(self):
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getSystemInfo(node)
    def testMasterGetNtcInfo(self):
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nNtc info for node %s:\n"%node
            print self.api.getNtcInfo(node)
    def testMasterMuteUnmute(self):
        print "\nTest mute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.MUTE)
        print "Muting...5s"
        #time.sleep(5)
        print "\nTest unmute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.UNMUTE)
if __name__ == "__main__":
    for times in range(0,100):
        print "CMD Stress Test %d"%times
        assert subprocess.call(['pgrep', '-x', 'ModemManager']) == 1
        suite = unittest.TestLoader().loadTestsFromTestCase(CmdStressTestCase)
        unittest.TextTestRunner(verbosity=2).run(suite)
