#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

#Thanks to Krisstian for teaching me how to join() and use xrange() in one-liner commands!

import indigo

import os
import sys

import fnmatch

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

########################################
# Tiny function to convert a list of integers (bytes in this case) to a
# hexidecimal string for pretty logging.
def convertListToHexStr(byteList):
	return ' '.join(["%02X" % byte for byte in byteList])

def convertListToStr(byteList):
	return ' '.join(["%02X" % byte for byte in byteList])

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)
		self.version = pluginVersion

		self.events = dict() # {} Need to define here any new Trigger types or the key throws undefined errors
		self.events["unlockedByCode"] = dict() 	# {} Need to define here any new Trigger types or the key throws undefined errors
		self.events["lockedByCode"] = dict()
		self.events["unlockedByMasterCode"] = dict()
		self.events["lockedByMasterCode"] = dict()
		self.events["invalidLimit"] = dict()
		self.events["invalidCode"] = dict()
		self.events["deadboltJammed"] = dict()
		self.events["unlockedManually"] = dict()
		self.events["lockedManually"] = dict()
		self.events["lockedManuallyOneTouch"] = dict()
		self.events["unlockedByController"] = dict()
		self.events["lockedByController"] = dict()
		self.events["unlockedByRF"] = dict()
		self.events["lockedByRF"] = dict()
		self.events["relockedAuto"] = dict()
		self.events["lockManuallyFailed"] = dict()
		self.events["lockRFFailed"] = dict()
		self.events["doorOpened"] = dict()
		self.events["doorClosed"] = dict()
		self.events["codeEntered"] = dict()

		self.eventKeys = dict()
		self.eventKeys["00"] = "[Caching]"
		self.eventKeys["01"] = "[Timeout]"
		self.eventKeys["02"] = "[Enter]"
		self.eventKeys["03"] = "[Disarm]"
		self.eventKeys["04"] = "[Arm]"
		self.eventKeys["05"] = "[Arm_Away]"
		self.eventKeys["06"] = "[Arm_Home]"
		self.eventKeys["07"] = "[Exit Delay]"
		self.eventKeys["08"] = "[Arm_1]"
		self.eventKeys["09"] = "[Arm_2]"
		self.eventKeys["0A"] = "[Arm_3]"
		self.eventKeys["0B"] = "[Arm_4]"
		self.eventKeys["0C"] = "[Arm_5]"
		self.eventKeys["0D"] = "[Arm_6]"
		self.eventKeys["0E"] = "[RFID]"
		self.eventKeys["0F"] = "[Bell]"
		self.eventKeys["10"] = "[Fire]"
		self.eventKeys["11"] = "[Police]"
		self.eventKeys["12"] = "[Panic]"
		self.eventKeys["13"] = "[Medical]"
		self.eventKeys["14"] = "[Open/Up]"
		self.eventKeys["15"] = "[Close/Down]"
		self.eventKeys["16"] = "[Lock]"
		self.eventKeys["17"] = "[Unlock]"
		self.eventKeys["18"] = "[Test]"
		self.eventKeys["19"] = "[Cancel]"

		self.lockIDs = list()

		self.zedFromDev = dict()
		self.zedFromNode = dict()
		self.devFromZed = dict()
		self.devFromNode = dict()
		self.nodeFromZed = dict()
		self.nodeFromDev = dict()

	########################################
	def startup(self):
		self.debugLog(u"startup called")
		self.debugLog("Plugin version: {}".format(self.version))
		indigo.zwave.subscribeToIncoming()

	def shutdown(self):
		self.debugLog(u"shutdown called")

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# Since the dialog closed we want to set the debug flag - if you don't directly use
		# a plugin's properties (and for debugLog we don't) you'll want to translate it to
		# the appropriate stuff here.
		if not userCancelled:
			self.debug = valuesDict.get("showDebugInfo", False)
			if self.debug:
				indigo.server.log("Debug logging enabled")
			else:
				indigo.server.log("Debug logging disabled")

	def deviceStartComm(self, dev):
		dev.stateListOrDisplayStateIdChanged()
		if (dev.deviceTypeId == "doorLock"):
			devID = dev.id																							#devID is the Indigo ID of my dummy device
			zedID = dev.ownerProps['deviceId']													#zedID is the Indigo ID of the actual ZWave device
			nodeID = indigo.devices[int(zedID)].ownerProps['address']		#nodeID is the ZWave Node ID

			self.zedFromDev[int(devID)] = int(zedID)
			self.zedFromNode[int(nodeID)] = int(zedID)
			self.devFromZed[int(zedID)] = int(devID)
			self.devFromNode[int(nodeID)] = int(devID)
			self.nodeFromZed[int(zedID)] = int(nodeID)
			self.nodeFromDev[int(devID)] = int(nodeID)

			self.lockIDs.append(nodeID)
		elif (dev.deviceTypeId == "keyPad"):
			devID = dev.id																							#devID is the Indigo ID of my dummy device
			zedID = dev.ownerProps['deviceId']													#zedID is the Indigo ID of the actual ZWave device
			nodeID = indigo.devices[int(zedID)].ownerProps['address']		#nodeID is the ZWave Node ID

			self.zedFromDev[int(devID)] = int(zedID)
			self.zedFromNode[int(nodeID)] = int(zedID)
			self.devFromZed[int(zedID)] = int(devID)
			self.devFromNode[int(nodeID)] = int(devID)
			self.nodeFromZed[int(zedID)] = int(nodeID)
			self.nodeFromDev[int(devID)] = int(nodeID)

			self.lockIDs.append(nodeID)

	def deviceStopComm(self, dev):
		if (dev.deviceTypeId == "doorLock"):
			devID = dev.id
			zedID = dev.ownerProps['deviceId']
			nodeID = indigo.devices[int(zedID)].ownerProps['address']

			self.zedFromDev.pop(int(devID),None)
			self.zedFromNode.pop(int(nodeID),None)
			self.devFromZed.pop(int(zedID),None)
			self.devFromNode.pop(int(nodeID),None)
			self.nodeFromZed.pop(int(zedID),None)
			self.nodeFromDev.pop(int(devID),None)

			self.lockIDs.remove(nodeID)
		elif (dev.deviceTypeId == "keyPad"):
			devID = dev.id
			zedID = dev.ownerProps['deviceId']
			nodeID = indigo.devices[int(zedID)].ownerProps['address']

			self.zedFromDev.pop(int(devID),None)
			self.zedFromNode.pop(int(nodeID),None)
			self.devFromZed.pop(int(zedID),None)
			self.devFromNode.pop(int(nodeID),None)
			self.nodeFromZed.pop(int(zedID),None)
			self.nodeFromDev.pop(int(devID),None)

			self.lockIDs.remove(nodeID)


	def setUserPin(self, pluginAction):
		self.debugLog("setUserPin action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		userNo = str(pluginAction.props["userNo"])
		userPin = str(self.substitute(str(pluginAction.props["userPin"])))

		self.setPin(userNo,userPin,indigoDev)
		#if len(userPin) not in [4,6,8,32]:
			#self.errorLog(u"This plugin only supports 4, 6 or 8 digit PINs or 11 character RFID tags")
			#return

		#indigo.server.log("Setting PIN for user " + str(userNo) + " to: " + str(userPin))
		#codeStr = [99, 01, int(userNo), 01] + self.getPinStr(userPin)
		#indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def clearUserPin(self, pluginAction):
		self.debugLog("clearUserPin action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		userNo = str(pluginAction.props["userNo"])

		self.clearPin(userNo,indigoDev)

		#indigo.server.log("Clearing PIN for user " + userNo)
		#codeStr = [99, 01, int(userNo), 00]
		#indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def getUserPin(self, pluginAction):
		self.debugLog("getUserPin action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		userNo = str(pluginAction.props["userNo"])

		self.getPin(userNo,indigoDev)

		#indigo.server.log("Requesting PIN for user " + userNo)
		#codeStr = [99, 02, int(userNo)]
		#indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def getModeIDLock(self,pluginAction):
		self.debugLog("getModeIDLock action called")
		indigoDev = pluginAction.deviceId

		self.debugLog(str(self.nodeFromDev))
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Requesting Lock Mode")

		codeStr = [112, 5, 1] #112 = 0x70 Configuration, 5 = 0x05 GET

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)


	def getPinStr(self,inPin):
		if len(inPin) in [4,5,6,7,8]:
			return [int(ord(inPin[i:i+1])) for i in range(0,len(inPin))]		#xrange in py2 is now range in py3
		elif len(inPin) == 29:
			return [int(inPin[i:i+2],16) for i in range(0,len(inPin),3)]		#range in py2 is now list(range()) in py3
		else:
			return []

	def setRTC(self, pluginAction):
		self.debugLog("setRCT action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		from datetime import datetime
		dt = datetime.now()

		dyear = dt.year
		dmonth = dt.month
		dday = dt.day
		dhour = dt.hour
		dmin = dt.minute
		dsec = dt.second

		yearBin = bin(dyear)[2:]
		self.debugLog(str(yearBin))

		yearHi = yearBin[0:3]
		yearLo = yearBin[3:]

		self.debugLog(str(yearHi))
		self.debugLog(str(int(yearHi,2)))
		self.debugLog(str(yearLo))
		self.debugLog(str(int(yearLo,2)))

		yearAgain = yearHi + yearLo
		yearAgain = str(int(yearAgain,2))

		self.debugLog(yearAgain)

		codeStr = [139, 1, int(yearHi,2), int(yearLo,2), dmonth, dday, dhour, dmin, dsec]

		indigo.server.log(u"Setting lock time to {}/{}/{} {}:{}:{} (UK format DD/MM/YYYY HH:MM:SS)".format(dday, dmonth, yearAgain, dhour, dmin, dsec))

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def setRelock(self, pluginAction):
		self.debugLog("setRelock action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		relockOn = str(pluginAction.props["relockOn"])
		relockTime = str(pluginAction.props["relockTime"])

		#self.debugLog(str(pluginAction.props))

		self.debugLog("Relock is: {}".format(relockOn))

		if relockOn == "on":
			indigo.server.log("Enabling auto relock mode with a timeout of {} seconds:".format(str(relockTime)))
			codeStr = [112, 4, 2, 1, 255]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))
			codeStr = [112, 4, 3, 1, int(relockTime)]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))
		else:
			indigo.server.log("Disabling auto relock mode")
			codeStr = [112, 4, 2, 1, 0]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def setWrongLimit(self, pluginAction):
		self.debugLog("setWrongLimit action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		wrongCount = str(pluginAction.props["wrongCount"])
		shutdownTime = str(pluginAction.props["shutdownTime"])

		indigo.server.log("Setting incorrect code limit to {} attempts with {} second timeout:".format(str(wrongCount),str(shutdownTime)))

		codeStr = [112, 4, 4, 1, int(wrongCount)]
		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		codeStr = [112, 4, 7, 1, int(shutdownTime)]
		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)


		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def setMode(self, pluginAction):
		self.debugLog("setMode action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		modeVal = str(pluginAction.props["modeVal"])

		indigo.server.log("Setting operating mode to {} :".format(modeVal))

		codeStr = [112, 4, 8, 1, int(modeVal)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def setModeIDLock(self, pluginAction):
		self.debugLog("setModeIDLock action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		modeVal = str(pluginAction.props["modeVal"])

		indigo.server.log("Setting operating mode to {} :".format(modeVal))

		codeStr = [112, 4, 1, 1, int(modeVal)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def sendCmdToRing(self, pluginAction):
		self.debugLog("sendCmdToRing action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo keypad selected: " + str(indigoDev))

		cmdToSend = str(pluginAction.props["cmdToSend"])

		indigo.server.log("Setting operating mode to {} :".format(cmdToSend))

		codeStr = [135, 1, int(cmdToSend)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))


########################################
	def zwaveCommandReceived(self, cmd):
		byteList = cmd['bytes']			# List of the raw bytes just received.
		byteListStr = convertListToHexStr(byteList)
		nodeId = cmd['nodeId']			# Can be None!
		endpoint = cmd['endpoint']		# Often will be None!

		bytes = byteListStr.split()
		nodeId = int(bytes[5],16)

		if (nodeId == 444): #Set to 44 for Study Fan Debugging
			byteListStr = "01 10 00 04 00 2C 0A 6F 01 11 02 02 04 31 32 33 34 FF"
			bytes = byteListStr.split()
			#This forces code below in 6F 01 to execute

		if (int(bytes[5],16)) not in self.lockIDs:
			#self.debugLog(u"Node {} is not a lock or keypad - ignoring".format(int(bytes[5],16)))
			return
		else:
			self.debugLog(u"Node ID {} (Hex {}) found in lockIDs".format((int(bytes[5],16)),(int(bytes[5],16))))

		#bytes = byteListStr.split()

		#if ((bytes[5] == "04") or (bytes[5] == "00")):			#Add node IDs here for debugging
			#self.debugLog(u"Raw command: {}".format(byteListStr))
			#if (bytes[9] == "00"):
				#self.updateState(int(bytes[5],16),"lockState","Open")
			#else:
				#self.updateState(int(bytes[5],16),"lockState","Closed")

		if (bytes[7] == "71") and (bytes[8] == "05") and (bytes[9] != "00"): #COMMAND_CLASS_ALARM v1/v2 = Lock Status
			#self.debugLog(u"-----")
			#self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Raw:  {}".format(byteListStr))
			#self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			#self.debugLog(u"Type:  {}".format(int(bytes[9],16)))
			#self.debugLog(u"User:  {}".format(int(bytes[10],16)))
			if (bytes[9] == "70"):
				indigo.server.log(u"Status: User {} updated [Node: {}]".format(int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "71"):
				indigo.server.log(u"Status: Updating user {} failed - PIN already exists [Node: {}]".format(int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "09"):
				indigo.server.log(u"Status: Deadbolt jammed on door [Node: {}]".format(int(bytes[5],16)))
				self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
			elif (bytes[9] == "12"):
				indigo.server.log(u"Status: User {} locked door [Node: {}]".format(int(bytes[10],16), int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Locked")
				self.updateState(int(bytes[5],16),"lastUser",int(bytes[10],16))
				if (int(bytes[10],16) == 251):
					self.triggerEvent("lockedByMasterCode",int(bytes[5],16),int(bytes[10],16))
				else:
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[10],16))
			elif (bytes[9] == "13"):
				indigo.server.log(u"Status: User {} unlocked door [Node: {}]".format(int(bytes[10],16), int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
				self.updateState(int(bytes[5],16),"lastUser",int(bytes[10],16))
				if (int(bytes[10],16) == 251):
					self.triggerEvent("unlockedByMasterCode",int(bytes[5],16),int(bytes[10],16))
					self.triggerEvent("unlockedByCodeIncMaster",int(bytes[5],16),int(bytes[10],16))
				else:
					self.triggerEvent("unlockedByCode",int(bytes[5],16),int(bytes[10],16))
			elif (bytes[9] == "15"):
				self.updateState(int(bytes[5],16),"lockState","Locked")
				if (bytes[10] == "01"):
					indigo.server.log(u"Status: Door locked manually [Node: {}]".format(int(bytes[5],16)))
					self.triggerEvent("lockedManually",int(bytes[5],16),"")
				elif (bytes[10] == "02"):
					indigo.server.log(u"Status: Door locked manually (one-touch button) [Node: {}]".format(int(bytes[5],16)))
					self.triggerEvent("lockedManuallyOneTouch",int(bytes[5],16),"")
			elif (bytes[9] == "16"):
				indigo.server.log(u"Status: Door unlocked manually [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
				self.triggerEvent("unlockedManually",int(bytes[5],16),"")
			elif (bytes[9] == "17"):
				indigo.server.log(u"Status: Door locked but bolt not fully extended [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Jammed")
				self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
			elif (bytes[9] == "18"):
				indigo.server.log(u"Status: Door locked by Indigo [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Locked")
				self.triggerEvent("lockedByController",int(bytes[5],16),"")
			elif (bytes[9] == "19"):
				indigo.server.log(u"Status: Door unlocked by Indigo [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
				self.triggerEvent("unlockedByController",int(bytes[5],16),"")
			elif (bytes[9] == "21"):
				indigo.server.log(u"Status: User {} removed from door [Node: {}]".format(int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "A1"):
				if (bytes[10] == "01"):
					indigo.server.log(u"Status: Invalid code limit exceeded [Node: {}]".format(int(bytes[5],16)))
					self.triggerEvent("invalidLimit",int(bytes[5],16),"")
				elif (bytes[10] == "02"):
					indigo.server.log(u"Status: Lock tamper alarm [Node: {}]".format(int(bytes[5],16)))
			elif (bytes[9] == "1B"):
				indigo.server.log(u"Status: Door re-locked automatically [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Locked")
				self.triggerEvent("relockedAuto",int(bytes[5],16),"")
			elif (bytes[9] == "A7"):
				indigo.server.log(u"Status: Low Battery [Node: {}]".format(int(bytes[5],16)))
			elif (bytes[9] == "A8"):
				indigo.server.log(u"Status: Critically Low Battery [Node: {}]".format(int(bytes[5],16)))
			elif (bytes[9] == "A9"):
				indigo.server.log(u"Status: Battery too low to operate [Node: {}]".format(int(bytes[5],16)))
			elif (bytes[9] == "82"):
				indigo.server.log(u"Status: Batteries replaced - please reset the internal clock [Node: {}]".format(int(bytes[5],16)))
			else:
				indigo.server.log(u"Unknown lock status received: {} [Node: {}]".format(int(bytes[9],16), int(bytes[5],16)))
			self.debugLog(u"-----")

		if (bytes[7] == "71") and (bytes[8] == "05") and (bytes[9] == "00"): #COMMAND_CLASS_NOTIFICATION (aka ALARM) v3 = Lock Status
			self.debugLog(u"-----")
			self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Raw:   {}".format(byteListStr))
			self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			self.debugLog(u"Type:  {}".format(int(bytes[13],16)))
			self.debugLog(u"Event: {}".format(int(bytes[14],16)))
			#self.debugLog(u"User:  {}".format(int(bytes[16],16)))	#Don't uncomment this line as byte 16 rarely exists
			if (bytes[13] == "06"): #Access Control
				if (bytes[14] == "01"):
					indigo.server.log(u"Status: Door locked manually [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Locked")
					self.triggerEvent("lockedManually",int(bytes[5],16),"")
				elif (bytes[14] == "02"):
					indigo.server.log(u"Status: Door unlocked manually [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
					self.triggerEvent("unlockedManually",int(bytes[5],16),"")
				elif (bytes[14] == "03"):
					indigo.server.log(u"Status: Door locked by RF [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Locked")
					self.triggerEvent("lockedByRF",int(bytes[5],16),"")
				elif (bytes[14] == "04"):
					indigo.server.log(u"Status: Door unlocked by RF [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
					self.triggerEvent("unlockedByRF",int(bytes[5],16),"")
				elif (bytes[14] == "05"):
					indigo.server.log(u"Status: Door locked by user {} [Node: {}]".format(int(bytes[16],16),int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Locked")
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[16],16))
				elif (bytes[14] == "06"):
					indigo.server.log(u"Status: Door unlocked by user {} [Node: {}]".format(int(bytes[16],16),int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
					self.triggerEvent("unlockedByCode",int(bytes[5],16),int(bytes[16],16))
				elif (bytes[14] == "07"):
					indigo.server.log(u"Status: Door failed to lock manually [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
					self.triggerEvent("lockManuallyFailed",int(bytes[5],16),"")
				elif (bytes[14] == "08"):
					indigo.server.log(u"Status: Door failed to lock by RF [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
					self.triggerEvent("lockRFFailed",int(bytes[5],16),"")
				elif (bytes[14] == "09"):
					indigo.server.log(u"Status: Door re-locked automatically [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Locked")
					self.triggerEvent("relockedAuto",int(bytes[5],16),"")
				elif (bytes[14] == "0A"):
					indigo.server.log(u"Status: Door failed to relock automatically [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "0B"):
					indigo.server.log(u"Status: Door lock jammed [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Jammed")
					self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
				elif (bytes[14] == "0C"):
					indigo.server.log(u"Status: All codes deleted [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0D"):
					indigo.server.log(u"Status: User code deleted [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0E"):
					indigo.server.log(u"Status: New user code added [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0F"):
					indigo.server.log(u"Status: Updating user failed - PIN already exists [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "10"):
					indigo.server.log(u"Status: Keypad temporarily disabled [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "11"):
					indigo.server.log(u"Status: Keypad in use [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "12"):
					indigo.server.log(u"Status: Master Code updated [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "13"):
					indigo.server.log(u"Status: Invalid code limit exceeded [Node: {}]".format(int(bytes[5],16)))
					self.triggerEvent("invalidLimit",int(bytes[5],16),"")
				elif (bytes[14] == "14"):
					indigo.server.log(u"Status: Invalid user code entered when unlocking door [Node: {}]".format(int(bytes[5],16)))
					self.triggerInvalidCode(int(bytes[5],16),"")
				elif (bytes[14] == "15"):
					indigo.server.log(u"Status: Invalid user code entered when locking door [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "16"):
					indigo.server.log(u"Status: Door is open [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Open")
					self.triggerEvent("doorOpened",int(bytes[5],16),"")
				elif (bytes[14] == "17"):
					indigo.server.log(u"Status: Door is closed [Node: {}]".format(int(bytes[5],16)))
					self.updateState(int(bytes[5],16),"lockState","Closed")
					self.triggerEvent("doorClosed",int(bytes[5],16),"")
			elif (bytes[13] == "07"): #Home Security
				if (bytes[14] == "01"):
					indigo.server.log(u"Status: Previous alarm/event cleared [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "02"):
					indigo.server.log(u"Status: Intrusion alert [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "03"):
					indigo.server.log(u"Status: Intrusion alert [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "04"):
					indigo.server.log(u"Status: Lock tamper switch activated [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "05"):
					indigo.server.log(u"Status: Attempted tamper: invalid code entered {} [Node: {}]".format(int(bytes[16],16),int(bytes[5],16)))
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[16],16))
				elif (bytes[14] == "06"):
					indigo.server.log(u"Status: Glass break detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "07"):
					indigo.server.log(u"Status: Motion detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "08"):
					indigo.server.log(u"Status: Motion detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "09"):
					indigo.server.log(u"Status: Tamper alert: lock motion detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0A"):
					indigo.server.log(u"Status: Impact detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0B"):
					indigo.server.log(u"Status: Magnetic field interference detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "0C"):
					indigo.server.log(u"Status: RF Jamming detected [Node: {}]".format(int(bytes[5],16)))
				elif (bytes[14] == "FE"):
					indigo.server.log(u"Status: Unknown alarm event [Node: {}]".format(int(bytes[5],16)))

		if (bytes[7] == "63") and (bytes[8] == "03"): #COMMAND_CLASS_USER_CODE = User Code status
			self.debugLog(u"-----")
			self.debugLog(u"User Code Status received:")
			self.debugLog(u"Raw command: {}".format(byteListStr))
			self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			self.debugLog(u"User:  {}".format(int(bytes[9],16)))
			if (bytes[10] == "01"): #Code is set/slot is occupied
				if len(bytes) < 22: # Code with characters
					retCode = ' '.join([chr(int(bytex, 16)) for bytex in bytes[11:len(bytes)-1]])
				else: # Pin or RFID tag
					retCode = ' '.join(bytes[11:len(bytes)-1])
				indigo.server.log(u"Status:  User code {} is {} [Node: {}]".format(int(bytes[9],16), retCode, int(bytes[5],16)))
			else:
				indigo.server.log(u"Status:  User code {} is blank [Node: {}]".format(int(bytes[9],16),int(bytes[5],16)))
			self.debugLog(u"-----")

		if (bytes[7] == "62") and (bytes[8] == "03"): #COMMAND_CLASS_DOOR = Door Lock Status
			#self.debugLog(u"-----")
			#self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Door: {}".format(byteListStr))
			self.debugLog("")
			self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			self.debugLog(u"Type:  {}".format(int(bytes[9],16)))
			self.debugLog(u"User:  {}".format(int(bytes[10],16)))
			if (bytes[9] == "00"):
				indigo.server.log(u"Status: Door is unlocked [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "01"):
				indigo.server.log(u"Status: Door is unlocked: auto relock active [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "10"):
				indigo.server.log(u"Status: Door is unlocked on the inside [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "11"):
				indigo.server.log(u"Status: Door is unlocked on the inside: auto relock active [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "20"):
				indigo.server.log(u"Status: Door is unlocked on the outside [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "21"):
				indigo.server.log(u"Status: Door is unlocked on the outside: auto relock active [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "FE"):
				indigo.server.log(u"Status: Door lock state unknown [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unknown")
			elif (bytes[9] == "FF"):
				indigo.server.log(u"Status: Door is locked [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Locked")
			if (bytes[11] == "00"): #Latch, Bold, Door status by binary bitmask
				indigo.server.log(u"Latch open, Bolt locked, Door open [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "01"):
				indigo.server.log(u"Latch open, Bolt locked, Door closed [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "02"):
				indigo.server.log(u"Latch open, Bolt unlocked, Door open [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "03"):
				indigo.server.log(u"Latch open, Bolt unlocked, Door closed [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "04"):
				indigo.server.log(u"Latch closed, Bolt locked, Door open [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "05"):
				indigo.server.log(u"Latch closed, Bolt locked, Door closed [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "06"):
				indigo.server.log(u"Latch closed, Bolt unlocked, Door open [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "07"):
				indigo.server.log(u"Latch closed, Bolt unlocked, Door closed [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")

		if (bytes[7] == "70") and (bytes[9] == "01"): #COMMAND_CLASS_CONFIGURATION (Param 1) = Door Lock Mode (eg Away)
			#self.debugLog(u"-----")
			#self.debugLog(u"Door Mode Report received:")
			self.debugLog(u"Door Mode: {}".format(byteListStr))
			self.debugLog("")
			self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			self.debugLog(u"Mode:  {}".format(int(bytes[11],16)))
			if (bytes[11] == "00"):
				indigo.server.log(u"Status: Door Mode is Home-ManualLock [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"doorMode","Home-Manual")
			elif (bytes[11] == "01"):
				indigo.server.log(u"Status: Door Mode is Home-AutoLock [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"doorMode","Home-Manual")
			elif (bytes[11] == "02"):
				indigo.server.log(u"Status: Door Mode is Away-ManualLock [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"doorMode","Home-Manual")
			elif (bytes[11] == "03"):
				indigo.server.log(u"Status: Door Mode is Away-Autolock [Node: {}]".format(int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"doorMode","Home-Manual")

		if (bytes[7] == "6F") and (bytes[8] == "01"): #COMMAND_CLASS_ENTRY_CONTROL = Keypad entry
			self.debugLog(u"-----")
			self.debugLog(u"Keypad entry code received:")
			self.debugLog(u"Raw command: {}".format(byteListStr))
			self.debugLog(u"Node:  {}".format(int(bytes[5],16)))
			if (bytes[10] == "02"): #01 = RAW, 02 = ASCII, 03 = MD5
				eventKey = bytes[11] #Enter, Arm, Disarm, etc
				codeVal = ''
				for bytex in bytes[13:len(bytes)-1]:
					codeVal = codeVal + str(int(bytex) - 30)
				self.debugLog(u"Code entered: {} {}".format(codeVal,self.eventKeys[eventKey]))
				self.triggerKeyCode(int(bytes[5],16),codeVal,eventKey)

	def testSet(self):
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x70,0x09,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)

	def testClear(self):
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x21,0x09,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)

	def testGet(self):
		cmd = {'bytes': [0x01,0x0E,0x00,0x04,0x00,0x2C,0x08,0x63,0x03,0x09,0x01,0x31,0x32,0x33,0x34,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0E,0x00,0x04,0x00,0x2C,0x08,0x63,0x03,0x09,0x01,0x31,0x32,0x33,0x34,0x35,0x36,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0E,0x00,0x04,0x00,0x2C,0x08,0x63,0x03,0x09,0x01,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0E,0x00,0x04,0x00,0x2C,0x08,0x63,0x03,0x09,0x01,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)


	def testHex(self):
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x13,0x01,0xFF], 'nodeId': None, 'endpoint': None} #Unlocked user 1
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x12,0x03,0xFF], 'nodeId': None, 'endpoint': None} #Locked user 3
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0xA1,0x01,0xFF], 'nodeId': None, 'endpoint': None} #Limit reached
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x09,0x01,0xFF], 'nodeId': None, 'endpoint': None} #Deadbolt jammed
		self.zwaveCommandReceived(cmd)
		cmd = {'bytes': [0x01,0x0A,0x00,0x04,0x00,0x2C,0x04,0x71,0x05,0x14,0x01,0xFF], 'nodeId': None, 'endpoint': None}
		self.zwaveCommandReceived(cmd)
		self.debugLog(u"lockIDs: {}".format(str(self.lockIDs)))


########################################
	def triggerStartProcessing(self, trigger):
		self.debugLog(u"Start processing trigger " + trigger.name)
		#self.debugLog(u"-----")
		self.events[str(trigger.pluginTypeId)][trigger.id] = trigger
		#self.debugLog(u"Trigger ID:     " + str(trigger.id))
		#self.debugLog(u"Lock Device:    " + str(trigger.pluginProps["deviceAddress"]))
		#self.debugLog(self.events)
		#self.debugLog(self.events[trigger.pluginTypeId])
		#self.debugLog(self.events[trigger.pluginTypeId][trigger.id])
		#self.debugLog(str(self.events["cmdReceived"][trigger.id].pluginProps["deviceAddress"]))
		devID = int(trigger.pluginProps["deviceAddress"])
		dev = indigo.devices[devID]
		#self.debugLog(str(dev))
		#self.debugLog(u"Z-Wave address: " + str(dev.ownerProps['address']))
		#self.debugLog(u"-----")
		#self.debugLog(u"")

	def triggerStopProcessing(self, trigger):
		self.debugLog(u"Stop processing trigger " + trigger.name)
		if trigger.pluginTypeId in self.events:
			if trigger.id in self.events[trigger.pluginTypeId]:
				del self.events[trigger.pluginTypeId][trigger.id]
		#self.debugLog(self.events)

	def triggerEvent(self,eventType,eventNode,userNo):
		#eventType is eg unlockedByCode, lockedByCode
		#eventNode is the ZWave Node ID (44)
		#userNo is the user's ID in the lock (User 1)
		self.debugLog(u"triggerEvent called: " + eventType)
		for trigger in self.events[eventType]:
			#dAddress is the Indigo device ID (12345678) of the dummy doorlock
			#dNodeID is the Indigo device's ZWave Node ID (44)
			dAddress = self.events[eventType][trigger].pluginProps["deviceAddress"]
			#dNodeID = indigo.devices[int(dAddress)].ownerProps['address']
			dNodeID = self.nodeFromDev[int(dAddress)]
			if (userNo != ""):
				dUserNo = self.events[eventType][trigger].pluginProps["userNo"]
			else:
				dUserNo = "" #We pass in "" as userNo if the trigger doesn't require a userNo match.
				#						 #We then match "" to "" below.
			self.debugLog(u"---")
			self.debugLog(u"dNodeID:   #{}#".format(dNodeID))
			self.debugLog(u"eventNode: #{}#".format(eventNode))
			self.debugLog(u"dUserNo:   #{}#".format(str(dUserNo)))
			self.debugLog(u"userNo:    #{}#".format(str(userNo)))
			if (str(eventNode) == str(dNodeID)):
				if ((str(dUserNo) == "Any") or (str(dUserNo) == str(userNo)) or ((str(dUserNo) == "AnyIncMaster") and (str(userNo) == "251"))):
					indigo.trigger.execute(trigger)
					self.debugLog(u"Executing trigger")

	def triggerInvalidCode(self,eventNode,inCode):
		#eventNode is the ZWave Node ID (44)
		#inCode is the wrongly entered code
		self.debugLog(u"triggerInvalidCode called")
		for trigger in self.events["invalidCode"]:
			#dAddress is the Indigo device ID (12345678) of the dummy doorlock
			#dNodeID is the Indigo device's ZWave Node ID (44)
			dAddress = self.events[eventType][trigger].pluginProps["deviceAddress"]
			#dNodeID = indigo.devices[int(dAddress)].ownerProps['address']
			dNodeID = self.nodeFromDev[int(dAddress)]
			dCode = self.events[eventType][trigger].pluginProps["invalidCode"]
			self.debugLog(u"---")
			self.debugLog(u"dNodeID:   #{}#".format(dNodeID))
			self.debugLog(u"eventNode: #{}#".format(eventNode))
			self.debugLog(u"dCode:   #{}#".format(str(dCode)))
			self.debugLog(u"inCode:    #{}#".format(str(inCode)))
			if (str(eventNode) == str(dNodeID)):
				if ((str(dCodeNo) == "") or (str(dCode) == str(inCode))):
					indigo.trigger.execute(trigger)
					self.debugLog(u"Executing trigger")

	def triggerKeyCode(self,eventNode,inCode,inKey):
		#eventNode is the ZWave Node ID (44)
		#inCode is the code entered
		#inKey is the event type or key pressed, eg Enter, Timeout
		self.debugLog(u"triggerKeyCode called")
		for trigger in self.events["codeEntered"]:
			#dAddress is the Indigo device ID (12345678) of the dummy keypad
			#dNodeID is the Indigo device's ZWave Node ID (44)
			dAddress = self.events["codeEntered"][trigger].pluginProps["deviceAddress"]
			#dNodeID = indigo.devices[int(dAddress)].ownerProps['address']
			dNodeID = self.nodeFromDev[int(dAddress)]
			dCode = self.events["codeEntered"][trigger].pluginProps["code"]
			dKey = self.events["codeEntered"][trigger].pluginProps["eventKey"]
			#self.debugLog(u"---")
			#self.debugLog(u"dNodeID:   #{}#".format(dNodeID))
			#self.debugLog(u"eventNode: #{}#".format(eventNode))
			#self.debugLog(u"dCode:   #{}#".format(str(dCode)))
			#self.debugLog(u"inCode:   #{}#".format(str(inCode)))
			#self.debugLog(u"dKey:    #{}#".format(str(dKey)))
			#self.debugLog(u"inKey:    #{}#".format(str(inKey)))
			if (str(eventNode) == str(dNodeID)):
				if ((str(inCode) == str(dCode)) and (str(inKey) == str(dKey))):
					indigo.trigger.execute(trigger)
					self.debugLog(u"Executing trigger")

	def setPin(self,userNo,userPin,indigoDev):
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Setting PIN for user " + str(userNo) + " to: " + str(userPin))

		codeStr = [99, 1, int(userNo), 1] + self.getPinStr(userPin)

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def clearPin(self,userNo,indigoDev):
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Clearing PIN for user " + userNo)

		codeStr = [99, 1, int(userNo), 0]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def getPin(self,userNo,indigoDev):
		self.debugLog(str(self.nodeFromDev))
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Requesting PIN for user " + userNo)

		codeStr = [99, 2, int(userNo)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)


	def updateState(self, nodeID, state, newState):
		self.debugLog("Updating state: {}".format(state))
		dev=indigo.devices[self.devFromNode[nodeID]]
		dev.updateStateOnServer(state, newState)

