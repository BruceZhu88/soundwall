#!/usr/bin/python
import unittest
import subprocess
import time
from lib import soundwallapi
from lib import EqData
from gpb import soundwall_pb2
from gpb import dsp_pb2

BTL_VERSION = "2.0.2"
APP_VERSION = "5.1.8.0"
DSP_VERSION = "4.2.2"
DOWN_DSP_VERSION = "1.2.2"
DOWN_APP_VERSION = "5.1.4.0"
TEST_SCRIPT_VERSION = "1.0.3"

class SoundwallTestCase(unittest.TestCase):
    def setUp(self):
        self.api = soundwallapi.SoundwallApi()
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)

    def tearDown(self):
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        self.api.close()

    def setA2BMode(self, mode):
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
	assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
	currentMode = self.api.getA2BMode()
	standalone = soundwall_pb2.A2Bmode.A2B_STANDALONE
	master = soundwall_pb2.A2Bmode.A2B_MASTER
	slave = soundwall_pb2.A2Bmode.A2B_SLAVE
	MODE = {"standalone":standalone, "master":master, "slave":slave}
	if MODE[mode] == currentMode:
            print "Soundwall already is",mode   
            return		
	print "Set soundwall to",mode
	self.api.setA2BMode(MODE[mode])
	self.api.systemRestart()
	self.api.close()
	#print "Waiting for soundwall to restart..."
	self.api.open()
	assert subprocess.call(['pgrep', '-x', 'ModemManager']) == 1
	assert self.api.getA2BMode() == MODE[mode]
	assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING	

class SetSoundModeTestCase(SoundwallTestCase):
    def testMasterBassAndRoomEQ(self):
	'''soundwall=master'''
	self.setA2BMode("master")
	startIndex = 0
	totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	EQ_0 = EqData.BassAndRoomEQ_0
	EQ_1 = EqData.BassAndRoomEQ_1
	bass_gain_0 = EqData.bass_gain_0
	bass_gain_1 = EqData.bass_gain_1
	RoomEQ = {0:EQ_0, 1:EQ_1}
	bass_gain = {0:bass_gain_0, 1:bass_gain_1}
	for selectEQ in range(1, -1, -1):
            print "Set soundwall BassAndRoomEQ_%s"%selectEQ
	    for node in range(0, totalNodes):
                print "Set BassAndRoomEQ to node",node
	        self.api.setBassAndRoomEQ(node, startIndex, bass_gain[selectEQ], RoomEQ[selectEQ])
		self.api.writeDspParam(node)
	        print self.api.getBassAndRoomEQ(node)
	    time.sleep(10)
	
    def testMasterDriverGain(self):
	'''soundwall=master'''
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	DriverGain_0 = EqData.DriverGain_0
        DriverGain_1 = EqData.DriverGain_1
        DriverGain = {0:DriverGain_0, 1:DriverGain_1}
        for selectDG in range(1, -1, -1):
	    print "Set soundwall GriverGainto node_%s"%selectDG
	    for node in range(0, totalNodes):
		print "Set DriverGain to node ",node
		self.api.setDriverGain(node,DriverGain[selectDG])
		print self.api.getDriverGain(node)
	    time.sleep(10)

    def testMasterGainAndDelay(self):
	'''soundwall=master'''
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	GainAndDelay_0 = EqData.GainAndDelay_0
        GainAndDelay_1 = EqData.GainAndDelay_1
        GainAndDelay = {0:GainAndDelay_0, 1:GainAndDelay_1}
        for selectGD in range(1, -1, -1):
	    print "Set soundwall GainAndDelay to node_%s"%selectGD
	    for node in range(0, totalNodes):
	        print "Set GainAndDelay to node ",node
	        self.api.setGainAndDelay(node,GainAndDelay[selectGD])
	        print self.api.getGainAndDelay(node)
	    time.sleep(10)

class GetSoundModeTestCase(SoundwallTestCase):
    def testMasterGetGainAndDelay(self):
	self.setA2BMode("master")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getGainAndDelay(node)

    def testMasterGetDriverGain(self):
	self.setA2BMode("master")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getDriverGain(node)

    def testMasterGetBassAndRoomEQ(self):
	self.setA2BMode("master")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getBassAndRoomEQ(node)

    def testSlaveGetGainAndDelay(self):
	self.setA2BMode("slave")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getGainAndDelay(node)

    def testSlaveGetDriverGain(self):
	self.setA2BMode("slave")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getDriverGain(node)

    def testSlaveGetBassAndRoomEQ(self):
	self.setA2BMode("slave")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getBassAndRoomEQ(node)

    def testStandaloneGetGainAndDelay(self):
	self.setA2BMode("standalone")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getGainAndDelay(node)

    def testStandaloneGetDriverGain(self):
	self.setA2BMode("standalone")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getDriverGain(node)

    def testStandaloneGetBassAndRoomEQ(self):
	self.setA2BMode("standalone")
	totalNodes = self.api.getTotalNodes()
	assert totalNodes > 0
	for node in range(0, totalNodes):
	    print self.api.getBassAndRoomEQ(node)

class PowerModeTestCase(SoundwallTestCase):
    def testMasterSetWorking(self):
        self.setA2BMode("master")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

    def testSlaveSetWorking(self):
        self.setA2BMode("slave")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

    def testStandaloneSetWorking(self):
        self.setA2BMode("standalone")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

    def testMasterSetStandby(self):
        self.setA2BMode("master")
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY

    def testSlaveSetStandby(self):
        self.setA2BMode("slave")
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY

    def testStandaloneSetStandby(self):
        self.setA2BMode("standalone")
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY

    def testMasterModeTransition(self):
        self.setA2BMode("master")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

    def testSlaveModeTransition(self):
        self.setA2BMode("slave")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

    def testStandaloneModeTransition(self):
        self.setA2BMode("standalone")
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING

class GetTotalNodesTestCase(SoundwallTestCase):
    def testMasterGetTotalNodes(self):
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	print "totalNodes=",totalNodes

    def testSlaveGetTotalNodes(self):
	self.setA2BMode("slave")
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
	print "totalNodes=",totalNodes

    def testStandaloneGetTotalNodes(self):
        self.setA2BMode("standalone")
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 0
        print "totalNodes=",totalNodes

class A2BModeTestCase(SoundwallTestCase):
    def testSetStandalone(self):
	self.setA2BMode("standalone")

    def testSetSlave(self):
	self.setA2BMode("slave")

    def testSetMaster(self):    
	self.setA2BMode("master")

    def testModeTransistion(self):
	self.setA2BMode("master")
	self.setA2BMode("slave")
        self.setA2BMode("standalone")

class FactoryResetTestCase(SoundwallTestCase):
    def testFactoryResetMaster(self):
	self.setA2BMode("master")
        self.api.factoryReset()
        self.api.close()
        print "Waiting for soundwall to restart..."
        self.api.open()
        assert self.api.getA2BMode() == soundwall_pb2.A2Bmode.A2B_SLAVE

    def testFactoryResetSlave(self):
	self.setA2BMode("slave")
        self.api.factoryReset()
        self.api.close()
        print "Waiting for soundwall to restart..."
        self.api.open()
        assert self.api.getA2BMode() == soundwall_pb2.A2Bmode.A2B_SLAVE
 
    def testFactoryResetStandalone(self):
        self.setA2BMode("standalone")
        self.api.factoryReset()
        self.api.close()
        print "Waiting for soundwall to restart..."
        self.api.open()
        assert self.api.getA2BMode() == soundwall_pb2.A2Bmode.A2B_SLAVE

class AudioInputTestCase(SoundwallTestCase):
    def testMasterTosLink(self):
	self.setA2BMode("master")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.TOS_LINK)

    def testSlaveTosLink(self):
	self.setA2BMode("slave")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.TOS_LINK)

    def testStandaloneTosLink(self):
	self.setA2BMode("standalone")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.TOS_LINK)

    def testMasterPowerLink(self):
	self.setA2BMode("master")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.POWER_LINK)

    def testSlavePowerLink(self):
	self.setA2BMode("slave")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.POWER_LINK)

    def testStandalonePowerLink(self):
	self.setA2BMode("standalone")
        self.api.setAudioInput(dsp_pb2.RequestAudioInput.POWER_LINK)

class SetToneTestCase(SoundwallTestCase):
    def testMasterSetTone(self):
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            for tile in range(1,5):
                print "This is tile %s, please input speaker!"%tile
                self.api.setTestTone(node, tile)
                time.sleep(2)
                self.api.setTestTone(node, 0)

    def testSlaveSetTone(self):
	self.setA2BMode("slave")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            for tile in range(1,5):
                print "This is tile %s, please input speaker!"%tile
                self.api.setTestTone(node, tile)
                time.sleep(2)
                self.api.setTestTone(node, 0)

    def testStandaloneSetTone(self):
	self.setA2BMode("standalone")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            for tile in range(1,5):
                print "This is tile %s, please input speaker!"%tile
                self.api.setTestTone(node, tile)
                time.sleep(6)
                self.api.setTestTone(node, 0)

class MuteModeTestCase(SoundwallTestCase):
    def testMasterMuteUnmute(self):
	self.setA2BMode("master")
        print "\nTest mute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.MUTE)
        print "Muting...5s"
        time.sleep(5)
        print "\nTest unmute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.UNMUTE)

    def testSlaveMuteUnmute(self):
	self.setA2BMode("slave")
        print "\nTest mute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.MUTE)
        print "Muting...5s"
        time.sleep(5)
        print "\nTest unmute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.UNMUTE)

    def testStandaloneMuteUnmute(self):
	self.setA2BMode("standalone")
        print "\nTest mute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.MUTE)
        print "Muting...5s"
        time.sleep(5)
        print "\nTest unmute mode"
        self.api.setMuteMode(soundwall_pb2.MuteMode.UNMUTE)

class GetSystemInfoTestCase(SoundwallTestCase):
    def testMasterGetSystemVersionInfo(self):
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getSystemInfo(node)

    def testSlaveGetSystemVersionInfo(self):
	self.setA2BMode("slave")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getSystemInfo(node)

    def testStandaloneGetSystemVersionInfo(self):
	self.setA2BMode("standalone")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getSystemInfo(node)

class GetNtcInfoTestCase(SoundwallTestCase):
    def testMasterGetNtcInfo(self):
	self.setA2BMode("master")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nNtc info for node %s:\n"%node
            print self.api.getNtcInfo(node)

    '''def testSlaveGetNtcInfo(self):
	self.setA2BMode("slave")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getNtcInfo(node)
    '''
    def testStandaloneGetNtcInfo(self):
	self.setA2BMode("standalone")
        totalNodes = self.api.getTotalNodes()
        for node in range(0, totalNodes):
            print "\nSystem info for node %s:\n"%node
            print self.api.getNtcInfo(node)

class UpgradeMasterTestCase(SoundwallTestCase):
    def setUp(self):
        self.api = soundwallapi.SoundwallApi()
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
        self.api.setA2BMode(soundwall_pb2.A2Bmode.A2B_MASTER)
        self.api.systemRestart()
        self.api.close()
        self.api.open()
    
    def tearDown(self):
        self.api.close()

    def testDFUUpgradeWhenWorking(self):
        self.api.open()
	self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
	assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
	self.api.close()
	assert subprocess.call(['./bin/fwupdate.sh', 'master']) == 0
	
    def testDFUUpgradeWhenInStandby(self):
	self.api.open()
	self.api.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
	assert self.api.getPowerMode() == soundwall_pb2.PowerMode.STANDBY
	self.api.close()
	assert subprocess.call(['./bin/fwupdate.sh', 'master']) == 0

    def testDFUDowngrade(self):
        self.api.open()
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
	assert self.api.getPowerMode() == soundwall_pb2.PowerMode.WORKING
	self.api.close()
        assert subprocess.call(['./bin/fwupdate.sh', 'down']) == 0
	self.api.open()
	systemInfo = self.api.getSystemInfo(0)
        # Update these whenever the version is changed
        assert systemInfo.module[3].version == BTL_VERSION
        assert systemInfo.module[4].version == DOWN_APP_VERSION
        assert systemInfo.module[5].version == DOWN_DSP_VERSION

class UpgradeSlavesTestCase(SoundwallTestCase):
    def setUp(self):
        self.api = soundwallapi.SoundwallApi()
        self.api.setPowerMode(soundwall_pb2.PowerMode.WORKING)
        self.api.setA2BMode(soundwall_pb2.A2Bmode.A2B_MASTER)
        self.api.systemRestart()
        self.api.close()

    def tearDown(self):
        self.api.close()

    def testSlaveUpgrade(self):
        self.api.open()
        slaveSystemInfo = self.api.getSystemInfo(1)
        self.api.close()
        if slaveSystemInfo.module[4].version == APP_VERSION:
            print "Downgrading to ", DOWN_APP_VERSION
            assert subprocess.call(['./bin/fwupdate.sh', 'down']) == 0
        else:
            print "Upgrading to ", APP_VERSION
            assert subprocess.call(['./bin/fwupdate.sh', 'master']) == 0
        self.api.open()
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 1
        for node in range(totalNodes-1, 0, -1):
            print "Upgrading slave node ", node
            event = self.api.upgradeSlave(node)
            assert event.nodeIndex == node
            assert event.eventId == 2 # D_EVENT_ID_FW_UPG_VIA_A2B
            assert event.eventParameter == 1 # Success
        # Verify the upgrade
        before = totalNodes
        after = self.api.getTotalNodes()
        assert before == after
        masterSystemInfo = self.api.getSystemInfo(0)
        node = totalNodes - 1
        while (node != 0):
            systemInfo = self.api.getSystemInfo(node)
            assert systemInfo.module[3].version == masterSystemInfo.module[3].version
            assert systemInfo.module[4].version == masterSystemInfo.module[4].version
            assert systemInfo.module[5].version == masterSystemInfo.module[5].version
            node = node - 1
     
    def testUpgradeAllSlaves(self):
        self.api.open()
        slaveSystemInfo = self.api.getSystemInfo(1)
        self.api.close()
        if slaveSystemInfo.module[4].version == APP_VERSION:
            print "Downgrading to ", DOWN_APP_VERSION
            assert subprocess.call(['./bin/fwupdate.sh', 'down']) == 0
        else:
            print "Upgrading to ", APP_VERSION
            assert subprocess.call(['./bin/fwupdate.sh', 'master']) == 0
        self.api.open()
        totalNodes = self.api.getTotalNodes()
        assert totalNodes > 1
        self.api.upgradeAllSlaves(totalNodes)
        # Verify the upgrade
        before = totalNodes
        after = self.api.getTotalNodes()
        assert before == after
        masterSystemInfo = self.api.getSystemInfo(0)
        node = totalNodes - 1
        while (node != 0):
            systemInfo = self.api.getSystemInfo(node)
            assert systemInfo.module[3].version == masterSystemInfo.module[3].version
            assert systemInfo.module[4].version == masterSystemInfo.module[4].version
            assert systemInfo.module[5].version == masterSystemInfo.module[5].version
            node = node - 1
        
if __name__ == "__main__":
    print "Running Soundwall test script version ", TEST_SCRIPT_VERSION
    assert subprocess.call(['pgrep', '-x', 'ModemManager']) == 1
    suite = unittest.TestLoader().loadTestsFromTestCase(MuteModeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(GetSystemInfoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(GetNtcInfoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(SetToneTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(AudioInputTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(FactoryResetTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(A2BModeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(GetTotalNodesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(PowerModeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # Always make sure to run the upgrade as the last 
    suite = unittest.TestLoader().loadTestsFromTestCase(UpgradeMasterTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(UpgradeSlavesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
