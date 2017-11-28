import os
import stat
import yahdlc
import time
import errno
import sys
import serial
from gpb import core_pb2
from gpb import ase_fep_pb2
from gpb import ase_fep_ReqResp_pb2
from gpb import soundwall_pb2
from gpb import common_pb2
from gpb import fep_ase_pb2

class SoundwallApi:
    def __init__(self):
        self.id = 0
        self.yahdlc = yahdlc.YAHDLC()
        self.open()

    def setId(self, id):
        self.id = id
 
    def close(self):
        self.f.close()
        # There will always be a race condition
        # when closing and opening the device
        # so to make sure we are not closing and opening
        # the device to quickly we have this sleep
        time.sleep(5)

    def devFileExists(self, path):
        try:
            return stat.S_ISCHR(os.stat(path).st_mode)
        except:
            return False

    def open(self):
        i=0
        result=False

        print "\nWaiting for device..",
        while result!=True:
            try:
                if self.devFileExists("/dev/soundwall"):
                    self.f = serial.Serial("/dev/soundwall", 115200)
                    result=True
            except IOError as e:
                if e.errno != errno.EBUSY and e.errno != errno.ENOENT:
                    print "error"
                    raise

            if i == 60:
                print "error"
                raise

            sys.stdout.write(".")
            sys.stdout.flush()

            i += 1
            time.sleep(1)
        print "ready"

    def waitForEvent(self):
        while not self.yahdlc.has_decode_frame():
            readValue = self.f.read(1)
            self.yahdlc.decode(readValue)
        frame_type, payload = self.yahdlc.get_decode_frame()
        assert frame_type == yahdlc.FrameType.DATA
        response = core_pb2.FepAseMessage()
        response.ParseFromString(payload)
        return response   
 
    def transact(self, request):
        # FYI!!! prints in this method can affect the test result
        # use prints in this only when debugging
        request.aseFepReq.id = self.id
        self.id += 1
        #print "GPB req: \n", request
        s = request.SerializeToString()
        self.yahdlc.start_encode_frame()
        self.yahdlc.add_payload_to_encode_frame(s)
        frame = self.yahdlc.finish_encode_frame()
        #print "yahdlc frame req: \n",
        i = 0
        for s in frame:
            i+=1
            #print "frame(%s)="%i, hex(ord(s))
        self.f.write(frame)
        #print "yahdlc frame ACK/NACK: \n",
        i = 0
	frame_type = None
	while frame_type != yahdlc.FrameType.ACK:
	    while not self.yahdlc.has_decode_frame():
	    	readValue = self.f.read(1)
	    	self.yahdlc.decode(readValue)
	    	i+=1
	    	#print "frame(%s)="%i, hex(ord(readValue))
	    frame_type, payload = self.yahdlc.get_decode_frame()

        #print "yahdlc fram payload: \n",
        i = 0
	while True: 
            while not self.yahdlc.has_decode_frame():
                readValue = self.f.read(1)
                self.yahdlc.decode(readValue)
                i+=1
                #print "frame(%s)="%i, hex(ord(readValue))
            frame_type, payload = self.yahdlc.get_decode_frame()
            assert frame_type == yahdlc.FrameType.DATA
            response = core_pb2.FepAseMessage()
            response.ParseFromString(payload)
	    if response.fepAseEvent.type == 0:
	        break
            #print "GPB resp: \n", response
        return response

    def setPowerMode(self, power_mode):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_POWER_MODE
        request.aseFepReq.reqPowerMode.mode = power_mode
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_POWER_MODE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def getPowerMode(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_POWER_MODE
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_POWER_MODE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('respPowerMode')
        return response.fepAseResp.respPowerMode.mode

    def setTotalNodes(self, totalNodes):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_TOTAL_NODES
	request.aseFepReq.nodeIndex.nodeIndex = totalNodes
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_TOTAL_NODES
	assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def getTotalNodes(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_TOTAL_NODES
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_TOTAL_NODES
        assert response.fepAseResp.HasField('respTotalNodes')
        return response.fepAseResp.respTotalNodes.totalNodes
 
    def setA2BMode(self, a2b_mode):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_A2B_MODE
        request.aseFepReq.reqA2Bmode.mode = a2b_mode
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_A2B_MODE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def getA2BMode(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_MODE
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_MODE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('respA2Bmode')
        return response.fepAseResp.respA2Bmode.mode

    def getA2BStatus(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_STATUS
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_STATUS
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('a2bStatus')
        return response.fepAseResp.a2bStatus.status

    def systemRestart(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SYSTEM_RESTART
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SYSTEM_RESTART
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        # Wait for the device to restart and wait for event
        time.sleep(5)

    def getSystemInfo(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_VERSION_INFO
        request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_VERSION_INFO
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('firmwareUpdateVersionInfo')
        return response.fepAseResp.firmwareUpdateVersionInfo

    def getNtcInfo(self, nodeIndex):
        request = core_pb2.AseFepMessage()
	request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_NTC_INFO
	request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_NTC_INFO
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('soundwallNtcInfo')
        return response.fepAseResp.soundwallNtcInfo

    def upgradeSlave(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        event = self.waitForEvent()
        print event
        assert event.fepAseEvent.HasField('diagnostic')
        assert event.fepAseEvent.type == fep_ase_pb2.Event.SOUNDWALL_DIAGNOSTIC
        assert event.fepAseEvent.diagnostic.nodeIndex == nodeIndex
	print "Successful upgrade of slave node", nodeIndex
        return event.fepAseEvent.diagnostic
 
    def upgradeAllSlaves(self, totalNodes):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        request.aseFepReq.nodeIndex.nodeIndex = 0xff
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        for node in range(totalNodes-1, 0, -1):
            print "Waiting for slave node ", node
            event = self.waitForEvent()
            print event
            assert event.fepAseEvent.HasField('diagnostic')
            assert event.fepAseEvent.type == fep_ase_pb2.Event.SOUNDWALL_DIAGNOSTIC
            assert event.fepAseEvent.diagnostic.nodeIndex == node
            assert event.fepAseEvent.diagnostic.eventId == 2 # D_EVENT_ID_FW_UPG_VIA_A2B
            assert event.fepAseEvent.diagnostic.eventParameter == 1 # Success
            print "Successful upgrade of slave node ", node

    def getA2BDfuFlag(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_DFU_FLAG
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_GET_A2B_DFU_FLAG
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('a2bDfuFlag')
        return response.fepAseResp.a2bDfuFlag.dfuFlag
 
    def enterDfu(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        request.aseFepReq.nodeIndex.nodeIndex = 0
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.FIRMWARE_UPDATE_SWITCH_TO_BOOTLOADER
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
     
    def factoryReset(self):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_FACTORY_RESET
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_FACTORY_RESET
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def setAudioInput(self, audio_input):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.AUDIO_INPUT
	request.aseFepReq.audioInput.input = audio_input
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.AUDIO_INPUT
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
   
    def setTestTone(self, nodeIndex, speakerTile):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_TEST_TONE
	request.aseFepReq.reqTestTone.nodeIndex = nodeIndex
	request.aseFepReq.reqTestTone.speakerTile = speakerTile
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_TEST_TONE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def setMuteMode(self, mute_mode):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_MUTE_MODE
        request.aseFepReq.muteMode.mode = mute_mode
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_MUTE_MODE
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def setGainAndDelay(self, nodeIndex,select):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_GAIN_AND_DELAY
        request.aseFepReq.reqGainAndDelay.nodeIndex = nodeIndex
	
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_L_1 = select['MT_TW_gain_L_1']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_R_1 = select['MT_TW_gain_R_1']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_L_2 = select['MT_TW_gain_L_2']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_R_2 = select['MT_TW_gain_R_2']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_L_3 = select['MT_TW_gain_L_3']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_R_3 = select['MT_TW_gain_R_3']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_L_4 = select['MT_TW_gain_L_4']
	request.aseFepReq.reqGainAndDelay.MT_TW_gain_R_4 = select['MT_TW_gain_R_4']

	request.aseFepReq.reqGainAndDelay.MT_TW_delay_L_1 = select['MT_TW_delay_L_1']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_R_1 = select['MT_TW_delay_R_1']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_L_2 = select['MT_TW_delay_L_2']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_R_2 = select['MT_TW_delay_R_2']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_L_3 = select['MT_TW_delay_L_3']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_R_3 = select['MT_TW_delay_R_3']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_L_4 = select['MT_TW_delay_L_4']
	request.aseFepReq.reqGainAndDelay.MT_TW_delay_R_4 = select['MT_TW_delay_R_4']

	request.aseFepReq.reqGainAndDelay.MUTE_L_R = select['MUTE_L_R']

        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_GAIN_AND_DELAY
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def setDriverGain(self, nodeIndex, select):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_DRIVER_GAIN
        request.aseFepReq.reqDriverGain.nodeIndex = nodeIndex

	request.aseFepReq.reqDriverGain.Tile_1_B_Cal_Gain = select['Tile_1_B_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_1_MT_Cal_Gain = select['Tile_1_MT_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_2_B_Cal_Gain = select['Tile_2_B_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_2_MT_Cal_Gain = select['Tile_2_MT_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_3_B_Cal_Gain = select['Tile_3_B_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_3_MT_Cal_Gain = select['Tile_3_MT_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_4_B_Cal_Gain = select['Tile_4_B_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_4_MT_Cal_Gain = select['Tile_4_MT_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_1_TW_Cal_Gain = select['Tile_1_TW_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_2_TW_Cal_Gain = select['Tile_2_TW_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_3_TW_Cal_Gain = select['Tile_3_TW_Cal_Gain']
	request.aseFepReq.reqDriverGain.Tile_4_TW_Cal_Gain = select['Tile_4_TW_Cal_Gain']

        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_DRIVER_GAIN
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def setBassAndRoomEQ(self, nodeIndex, startIndex, bass_gain, select):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_SET_BASS_AND_ROOMEQ
        request.aseFepReq.reqBassAndRoomEQ.nodeIndex = nodeIndex
	request.aseFepReq.reqBassAndRoomEQ.bass_gain = bass_gain
	request.aseFepReq.reqBassAndRoomEQ.startIndex = startIndex
	#eq0                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam0.b0 = select['eqParam0_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam0.b1 = select['eqParam0_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam0.b2 = select['eqParam0_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam0.a1 = select['eqParam0_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam0.a2 = select['eqParam0_a2']
        #eq1                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam1.b0 = select['eqParam1_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam1.b1 = select['eqParam1_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam1.b2 = select['eqParam1_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam1.a1 = select['eqParam1_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam1.a2 = select['eqParam1_a2']
        #eq2                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam2.b0 = select['eqParam2_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam2.b1 = select['eqParam2_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam2.b2 = select['eqParam2_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam2.a1 = select['eqParam2_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam2.a2 = select['eqParam2_a2']
        #eq3                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam3.b0 = select['eqParam3_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam3.b1 = select['eqParam3_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam3.b2 = select['eqParam3_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam3.a1 = select['eqParam3_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam3.a2 = select['eqParam3_a2']
        #eq4                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam4.b0 = select['eqParam4_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam4.b1 = select['eqParam4_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam4.b2 = select['eqParam4_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam4.a1 = select['eqParam4_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam4.a2 = select['eqParam4_a2']
        #eq5                                                                  
        request.aseFepReq.reqBassAndRoomEQ.eqParam5.b0 = select['eqParam5_b0']
        request.aseFepReq.reqBassAndRoomEQ.eqParam5.b1 = select['eqParam5_b1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam5.b2 = select['eqParam5_b2']
        request.aseFepReq.reqBassAndRoomEQ.eqParam5.a1 = select['eqParam5_a1']
        request.aseFepReq.reqBassAndRoomEQ.eqParam5.a2 = select['eqParam5_a2']
                        
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_SET_BASS_AND_ROOMEQ
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
	
    def writeDspParam(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_WRITE_DSP_PARAM
	request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.type == ase_fep_ReqResp_pb2.SOUNDWALL_WRITE_DSP_PARAM
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE

    def getGainAndDelay(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_GAIN_AND_DELAY
        request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('respGainAndDelay')
        return response.fepAseResp.respGainAndDelay

    def getDriverGain(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_DRIVER_GAIN
	request.aseFepReq.nodeIndex.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('respDriverGain')
        return response.fepAseResp.respDriverGain

    def getBassAndRoomEQ(self, nodeIndex):
        request = core_pb2.AseFepMessage()
        request.aseFepReq.type = ase_fep_ReqResp_pb2.SOUNDWALL_GET_BASS_AND_ROOMEQ
        request.aseFepReq.getBassAndRoomEQ.nodeIndex = nodeIndex
        response = self.transact(request)
        assert response.fepAseResp.genericResponse.status == common_pb2.GenericResponse.DONE
        assert response.fepAseResp.HasField('respBassAndRoomEQ')
        return response.fepAseResp.respBassAndRoomEQ

