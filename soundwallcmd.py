#!/usr/bin/python
import sys
import argparse
from lib import soundwallapi
from lib import EqData
from gpb import soundwall_pb2
from gpb import dsp_pb2

def main():
    parser = argparse.ArgumentParser(description='Run soundwall commands')

    parser.add_argument('--set-power-mode', action='store', choices=('standby', 'working'),
                        help='Set the power mode either standby or working')
    parser.add_argument('--get-power-mode', action='store_const', dest='get_power_mode', const='',
                        help='Get the power mode')
    parser.add_argument('--get-a2b-mode', action='store_const', dest='get_a2b_mode', const='',
                        help='Get the a2b mode')
    parser.add_argument('--get-a2b-status', action='store_const', dest='get_a2b_status', const='',
                        help='Get the a2b status')
    parser.add_argument('--set-a2b-mode', action='store', choices=('slave', 'master', 'standalone'),
                        help='Set the a2b mode either slave or master, will require a system restart')
    parser.add_argument('--system-restart', action='store_const', dest='system_restart', const='',
                        help='Restart system')
    parser.add_argument('--system-info', action='store', dest='get_system_info', type=int,
                        help='Get version info from node')
    parser.add_argument('--system-info-list', action='store_const', dest='get_system_info_list', const='',
                        help='Get version info from all nodes')
    parser.add_argument('--ntc-info', action='store', dest='get_ntc_info', type=int,
                        help='Get NTC info from node')
    parser.add_argument('--ntc-info-list', action='store_const', dest='get_ntc_info_list', const='',
                        help='Get NTC info from all nodes')
    parser.add_argument('--upgrade-slave', action='store', dest='upgrade_slave', type=int,
                        help='Upgrade node')
    parser.add_argument('--get-total-nodes', action='store_const', dest='total_nodes', const='',
                        help='Get total nodes in the system')
    parser.add_argument('--set-total-nodes', action='store', dest='set_total_nodes', type=int,
                        help='Set total nodes in the system')    
    parser.add_argument('--enter-dfu', action='store_const', dest='enter_dfu', const='',
                        help='Set master in DFU mode')
    parser.add_argument('--trigger-nack', action='store_const', dest='trigger_nack', const='',
                        help='Trigger NACK from the soundwall')
    parser.add_argument('--factory-reset', action='store_const', dest='factory_reset', const='',
                        help='Factory reset')
    parser.add_argument('--upgrade-all-slaves', action='store_const', dest='all_slaves', const='',
                        help='Upgrade all slaves')
    parser.add_argument('--get-a2b-dfu-flag', action='store_const', dest='a2b_dfu_flag', const='',
                        help='Get A2B Dfu flag')
    parser.add_argument('--test-tone-on', action='store', dest='test_tone_on', const=None, nargs='*',
                        help='Turn test tone on')
    parser.add_argument('--test-tone-off', action='store', dest='test_tone_off', const=None,
                        help='Turn test tone off')
    parser.add_argument('--set-mute-mode', action='store', choices=('mute', 'unmute'),
                        help='Set the audio output either mute or unmute')
    parser.add_argument('--set-source', action='store', choices=('toslink', 'powerlink'),
                        help='Set source either toslink or powerlink')
    parser.add_argument('--get-eq', action='store', dest='get_eq', type=int,
                        help='Get bassAndRoomEQ value')
    parser.add_argument('--get-drivergain', action='store', dest='get_drivergain', type=int,
                        help='Get driverGain value')
    parser.add_argument('--get-gainanddelay', action='store', dest='get_gainanddelay', type=int,
                        help='Get gainAndDelay value')
    parser.add_argument('--set-eq', action='store', dest='set_eq', type=int,
                        help='Set bassAndRoomEQ value')
    parser.add_argument('--set-drivergain', action='store', dest='set_drivergain', type=int,
                        help='Set driverGain value')
    parser.add_argument('--set-gainanddelay', action='store', dest='set_gainanddelay', type=int,
                        help='Set gainAndDelay value')
    parser.add_argument('--get-event', action='store_const', dest='get_event', const='',
                        help='Get event')
 
    args = parser.parse_args()    

    soundwall = soundwallapi.SoundwallApi()
    if args.set_power_mode is not None:
        if args.set_power_mode == 'standby':
            soundwall.setPowerMode(soundwall_pb2.PowerMode.STANDBY)
        elif args.set_power_mode == 'working':
            soundwall.setPowerMode(soundwall_pb2.PowerMode.WORKING)
    elif args.get_power_mode is not None:
        power_mode = soundwall.getPowerMode()
        if power_mode == soundwall_pb2.PowerMode.WORKING:
            print "working"
        elif power_mode == soundwall_pb2.PowerMode.STANDBY:
            print "standby"
    elif args.set_a2b_mode is not None:
        if args.set_a2b_mode == 'master':
            soundwall.setA2BMode(soundwall_pb2.A2Bmode.A2B_MASTER)
        elif args.set_a2b_mode == 'slave':
            soundwall.setA2BMode(soundwall_pb2.A2Bmode.A2B_SLAVE)
	elif args.set_a2b_mode == 'standalone':
	    soundwall.setA2BMode(soundwall_pb2.A2Bmode.A2B_STANDALONE)
    elif args.get_a2b_mode is not None:
        a2b_mode = soundwall.getA2BMode()
        if a2b_mode == soundwall_pb2.A2Bmode.A2B_SLAVE:
            print "slave"
        elif a2b_mode == soundwall_pb2.A2Bmode.A2B_MASTER:
            print "master"
    elif args.get_a2b_status is not None:
	status = soundwall.getA2BStatus()
	if status == soundwall_pb2.A2bStatus.A2B_STATUS_READY:
	    print "Ready"
	elif status == soundwall_pb2.A2bStatus.A2B_STATUS_INIT_IN_PROCESS:
            print "Init in progress"
	elif status == soundwall_pb2.A2bStatus.A2B_STATUS_ERROR:
            print "error"
    elif args.system_restart is not None:
        soundwall.systemRestart()
    elif args.get_system_info is not None:
        totalNodes = soundwall.getTotalNodes()
        assert args.get_system_info < totalNodes
        systemInfo = soundwall.getSystemInfo(args.get_system_info)
        totalNodes = soundwall.getTotalNodes()
        print systemInfo
    elif args.get_system_info_list is not None:
        totalNodes = soundwall.getTotalNodes()
        for node in range(0, totalNodes):
            print "System info for node %s:\n"%node
            print soundwall.getSystemInfo(node)
    elif args.get_ntc_info is not None:
        totalNodes = soundwall.getTotalNodes()
        assert args.get_ntc_info < totalNodes
        ntcInfo = soundwall.getNtcInfo(args.get_ntc_info)
        totalNodes = soundwall.getTotalNodes()
        print ntcInfo
    elif args.get_ntc_info_list is not None:
        totalNodes = soundwall.getTotalNodes()
        for node in range(0, totalNodes):
            print "Ntc info for node %s:\n"%node
            print soundwall.getNtcInfo(node)
    elif args.upgrade_slave is not None:
        node = args.upgrade_slave
        totalNodes = soundwall.getTotalNodes()
        assert node < totalNodes
        assert node > 0
        print soundwall.upgradeSlave(node)
    elif args.total_nodes is not None:
        print soundwall.getTotalNodes()
    elif args.set_total_nodes is not None:
	totalNodes = args.set_total_nodes
	assert totalNodes > 0 
	soundwall.setTotalNodes(totalNodes)
    elif args.enter_dfu is not None:
        soundwall.enterDfu()
    elif args.trigger_nack is not None:
        print "trigger nack"
        soundwall.setId(1)
        totalNodes = soundwall.getTotalNodes()
        systemInfo = soundwall.getSystemInfo(0)
	NtcInfo = soundwall.getSystemInfo(0)
        totalNodes = soundwall.getTotalNodes()
        print systemInfo
    elif args.factory_reset is not None:
        print soundwall.factoryReset()
    elif args.all_slaves is not None:
        totalNodes = soundwall.getTotalNodes()
        soundwall.upgradeAllSlaves(totalNodes)
    elif args.a2b_dfu_flag is not None:
        flag = soundwall.getA2BDfuFlag()
        if flag == 1:
            print "dfu"
        else:
            print "normal"
    elif args.test_tone_on is not None:
        totalNodes = soundwall.getTotalNodes()
        node = int(args.test_tone_on[0])
        speaker = int(args.test_tone_on[1])
        assert node < totalNodes
        assert node >= 0
        assert speaker > 0
	assert speaker <= 4
        soundwall.setTestTone(node, speaker)
    elif args.test_tone_off is not None:
        totalNodes = soundwall.getTotalNodes()
        node = int(args.test_tone_off)
        assert node < totalNodes
        assert node >= 0
        soundwall.setTestTone(node, 0)
    elif args.set_source is not None:
        if args.set_source == 'toslink':
            soundwall.setAudioInput(dsp_pb2.RequestAudioInput.TOS_LINK)
        elif args.set_source == 'powerlink':
            soundwall.setAudioInput(dsp_pb2.RequestAudioInput.POWER_LINK)
    elif args.get_event is not None:
	while 1:
	    print soundwall.waitForEvent()
    elif args.set_mute_mode is not None:
        if args.set_mute_mode == 'mute':
            soundwall.setMuteMode(soundwall_pb2.MuteMode.MUTE)
        elif args.set_mute_mode == 'unmute':
            soundwall.setMuteMode(soundwall_pb2.MuteMode.UNMUTE)
    elif args.get_gainanddelay is not None:
	totalNodes = soundwall.getTotalNodes()
	assert args.get_eq < totalNodes
	print soundwall.getGainAndDelay(args.get_gainanddelay)
    elif args.get_drivergain is not None:
	totalNodes = soundwall.getTotalNodes()
	assert args.get_eq < totalNodes
	print soundwall.getDriverGain(args.get_drivergain)
    elif args.get_eq is not None:
	totalNodes = soundwall.getTotalNodes()
        assert args.get_eq < totalNodes
	print soundwall.getBassAndRoomEQ(args.get_eq)
    elif args.set_eq is not None:
	assert args.set_eq < 2
	totalNodes = soundwall.getTotalNodes()
        assert totalNodes > 0
	startIndex = 0
        EQ_0 = EqData.BassAndRoomEQ_0
        EQ_1 = EqData.BassAndRoomEQ_1
        bass_gain_0 = EqData.bass_gain_0
        bass_gain_1 = EqData.bass_gain_1
        RoomEQ = {0:EQ_0, 1:EQ_1}
        bass_gain = {0:bass_gain_0, 1:bass_gain_1}
        for node in range(0, totalNodes):
            print "Set BassAndRoomEQ to node",node
            soundwall.setBassAndRoomEQ(node, startIndex, bass_gain[args.set_eq], RoomEQ[args.set_eq])
            soundwall.writeDspParam(node)
            print soundwall.getBassAndRoomEQ(node)
    elif args.set_drivergain is not None:
        totalNodes = soundwall.getTotalNodes()
        assert totalNodes > 0
	DriverGain_0 = EqData.DriverGain_0
        DriverGain_1 = EqData.DriverGain_1
        DriverGain = {0:DriverGain_0, 1:DriverGain_1}
        for node in range(0, totalNodes):
	    print "Set DriverGain to node ",node
            soundwall.setDriverGain(node,DriverGain[args.set_drivergain])
	    print soundwall.getDriverGain(node)
    elif args.set_gainanddelay is not None:
	totalNodes = soundwall.getTotalNodes()
        assert totalNodes > 0
	GainAndDelay_0 = EqData.GainAndDelay_0
        GainAndDelay_1 = EqData.GainAndDelay_1
        GainAndDelay = {0:GainAndDelay_0, 1:GainAndDelay_1}
        for node in range(0, totalNodes):
	    print "Set GainAndDelay to node ",node
	    soundwall.setGainAndDelay(node,GainAndDelay[args.set_gainanddelay])
	    print soundwall.getGainAndDelay(node)
	
	
if __name__ == "__main__":
    main()
