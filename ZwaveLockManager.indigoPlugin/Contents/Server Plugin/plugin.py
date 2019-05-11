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
		self.events["unlockedByController"] = dict()
		self.events["lockedByController"] = dict()
		self.events["unlockedByRF"] = dict()
		self.events["lockedByRF"] = dict()
		self.events["relockedAuto"] = dict()
		self.events["lockManuallyFailed"] = dict()
		self.events["lockRFFailed"] = dict()
		self.events["doorOpened"] = dict()
		self.events["doorClosed"] = dict()

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

	def getPinStr(self,inPin):
		if len(inPin) in [4,5,6,7,8]:
			return [int(ord(inPin[i:i+1])) for i in xrange(0,len(inPin))]
		elif len(inPin) == 29:
			return [int(inPin[i:i+2],16) for i in xrange(0,len(inPin),3)]
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

		codeStr = [139, 01, int(yearHi,2), int(yearLo,2), dmonth, dday, dhour, dmin, dsec]

		indigo.server.log(u"Setting lock time to %s/%s/%s %s:%s:%s (UK format DD/MM/YYYY HH:MM:SS)" % (dday, dmonth, yearAgain, dhour, dmin, dsec))

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def setRelock(self, pluginAction):
		self.debugLog("setRelock action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		relockOn = str(pluginAction.props["relockOn"])
		relockTime = str(pluginAction.props["relockTime"])

		if relockOn:
			indigo.server.log("Enabling auto relock mode with a timeout of %s seconds:" % str(relockTime))
			codeStr = [112, 04, 02, 01, 255]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))
			codeStr = [112, 04, 03, 01, int(relockTime)]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))
		else:
			indigo.server.log("Disabling auto relock mode")
			codeStr = [112, 04, 02, 01, 00]
			indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)
			#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def setWrongLimit(self, pluginAction):
		self.debugLog("setWrongLimit action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		wrongCount = str(pluginAction.props["wrongCount"])
		shutdownTime = str(pluginAction.props["shutdownTime"])

		indigo.server.log("Setting incorrect code limit to %s attempts with %s second timeout:" % (str(wrongCount),str(shutdownTime)))

		codeStr = [112, 04, 04, 01, int(wrongCount)]
		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		codeStr = [112, 04, 07, 01, int(shutdownTime)]
		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)


		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))

	def setMode(self, pluginAction):
		self.debugLog("setMode action called")
		indigoDev = pluginAction.deviceId
		self.debugLog("Indigo lock selected: " + str(indigoDev))

		modeVal = str(pluginAction.props["modeVal"])

		indigo.server.log("Setting operating mode to %s :" % modeVal)

		codeStr = [112, 4, 8, 1, int(modeVal)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

		#indigo.server.log("Sending raw command: [" + convertListToStr(codeStr) + "] to device " + str(indigoDev))




########################################
	def zwaveCommandReceived(self, cmd):
		byteList = cmd['bytes']			# List of the raw bytes just received.
		byteListStr = convertListToHexStr(byteList)
		nodeId = cmd['nodeId']			# Can be None!
		endpoint = cmd['endpoint']		# Often will be None!

		bytes = byteListStr.split()
		#nodeId = int(bytes[5],16)

		if (int(bytes[5],16)) not in self.lockIDs:
			#self.debugLog(u"Node %s is not a lock - ignoring" % (int(bytes[5],16)))
			return
		else:
			self.debugLog(u"Node ID %s (Hex %s) found in lockIDs" % ((int(bytes[5],16)),(int(bytes[5],16))))

		#bytes = byteListStr.split()

		#if ((bytes[5] == "04") or (bytes[5] == "00")):			#Add node IDs here for debugging
			#self.debugLog(u"Raw command: %s" % (byteListStr))
			#if (bytes[9] == "00"):
				#self.updateState(int(bytes[5],16),"lockState","Open")
			#else:
				#self.updateState(int(bytes[5],16),"lockState","Closed")

		if (bytes[7] == "71") and (bytes[8] == "05") and (bytes[9] != "00"): #COMMAND_CLASS_ALARM v1/v2 = Lock Status
			#self.debugLog(u"-----")
			#self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Raw:  %s" % (byteListStr))
			#self.debugLog(u"Node:  %s" % (int(bytes[5],16)))
			#self.debugLog(u"Type:  %s" % (int(bytes[9],16)))
			#self.debugLog(u"User:  %s" % (int(bytes[10],16)))
			if (bytes[9] == "70"):
				indigo.server.log(u"Status: User %s updated [Node: %s]" % (int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "71"):
				indigo.server.log(u"Status: Updating user %s failed - PIN already exists [Node: %s]" % (int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "09"):
				indigo.server.log(u"Status: Deadbolt jammed on door [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
			elif (bytes[9] == "12"):
				indigo.server.log(u"Status: User %s locked door [Node: %s]" % (int(bytes[10],16), int(bytes[5],16)))
				if (int(bytes[10],16) == 251):
					self.triggerEvent("lockedByMasterCode",int(bytes[5],16),int(bytes[10],16))
				else:
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[10],16))
				self.updateState(int(bytes[5],16),"lockState","Locked")
			elif (bytes[9] == "13"):
				indigo.server.log(u"Status: User %s unlocked door [Node: %s]" % (int(bytes[10],16), int(bytes[5],16)))
				if (int(bytes[10],16) == 251):
					self.triggerEvent("unlockedByMasterCode",int(bytes[5],16),int(bytes[10],16))
				else:
					self.triggerEvent("unlockedByCode",int(bytes[5],16),int(bytes[10],16))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "15"):
				if (bytes[10] == "01"):
					indigo.server.log(u"Status: Door locked manually [Node: %s]" % (int(bytes[5],16)))
					self.triggerEvent("lockedManually",int(bytes[5],16),"")
				elif (bytes[10] == "02"):
					indigo.server.log(u"Status: Door locked manually (one-touch button) [Node: %s]" % (int(bytes[5],16)))
					self.triggerEvent("lockedManually",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Locked")
			elif (bytes[9] == "16"):
				indigo.server.log(u"Status: Door unlocked manually [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("unlockedManually",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "17"):
				indigo.server.log(u"Status: Door locked but bolt not fully extended [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Jammed")
			elif (bytes[9] == "18"):
				indigo.server.log(u"Status: Door locked by Indigo [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("lockedByController",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Locked")
			elif (bytes[9] == "19"):
				indigo.server.log(u"Status: Door unlocked by Indigo [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("unlockedByController",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "21"):
				indigo.server.log(u"Status: User %s removed from door [Node: %s]" % (int(bytes[10],16), int(bytes[5],16)))
			elif (bytes[9] == "A1"):
				if (bytes[10] == "01"):
					indigo.server.log(u"Status: Invalid code limit exceeded [Node: %s]" % (int(bytes[5],16)))
					self.triggerEvent("invalidLimit",int(bytes[5],16),"")
				elif (bytes[10] == "02"):
					indigo.server.log(u"Status: Lock tamper alarm [Node: %s]" % (int(bytes[5],16)))
			elif (bytes[9] == "1B"):
				indigo.server.log(u"Status: Door re-locked automatically [Node: %s]" % (int(bytes[5],16)))
				self.triggerEvent("relockedAuto",int(bytes[5],16),"")
				self.updateState(int(bytes[5],16),"lockState","Locked")
			elif (bytes[9] == "A7"):
				indigo.server.log(u"Status: Low Battery [Node: %s]" % (int(bytes[5],16)))
			elif (bytes[9] == "A8"):
				indigo.server.log(u"Status: Critically Low Battery [Node: %s]" % (int(bytes[5],16)))
			elif (bytes[9] == "A9"):
				indigo.server.log(u"Status: Battery too low to operate [Node: %s]" % (int(bytes[5],16)))
			elif (bytes[9] == "82"):
				indigo.server.log(u"Status: Batteries replaced - please reset the internal clock [Node: %s]" % (int(bytes[5],16)))
			else:
				indigo.server.log(u"Unknown lock status received: %s [Node: %s]" % (int(bytes[9],16), int(bytes[5],16)))
			self.debugLog(u"-----")

		if (bytes[7] == "71") and (bytes[8] == "05") and (bytes[9] == "00"): #COMMAND_CLASS_NOTIFICATION (aka ALARM) v3 = Lock Status
			self.debugLog(u"-----")
			self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Raw:   %s" % (byteListStr))
			self.debugLog(u"Node:  %s" % (int(bytes[5],16)))
			self.debugLog(u"Type:  %s" % (int(bytes[13],16)))
			self.debugLog(u"Event: %s" % (int(bytes[14],16)))
			#self.debugLog(u"User:  %s" % (int(bytes[16],16)))	#Don't uncomment this line as byte 16 rarely exists
			if (bytes[13] == "06"): #Access Control
				if (bytes[14] == "01"):
					indigo.server.log(u"Status: Door locked manually [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("lockedManually",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Locked")
				elif (bytes[14] == "02"):
					indigo.server.log(u"Status: Door unlocked manually [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("unlockedManually",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "03"):
					indigo.server.log(u"Status: Door locked by RF [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("lockedByRF",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Locked")
				elif (bytes[14] == "04"):
					indigo.server.log(u"Status: Door unlocked by RF [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("unlockedByRF",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "05"):
					indigo.server.log(u"Status: Door locked by user %s [Node: %s]" % (int(bytes[16],16),int(bytes[5],16)))
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[16],16))
					self.updateState(int(bytes[5],16),"lockState","Locked")
				elif (bytes[14] == "06"):
					indigo.server.log(u"Status: Door unlocked by user %s [Node: %s]" % (int(bytes[16],16),int(bytes[5],16)))
					self.triggerEvent("unlockedByCode",int(bytes[5],16),int(bytes[16],16))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "07"):
					indigo.server.log(u"Status: Door failed to lock manually [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("lockManuallyFailed",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "08"):
					indigo.server.log(u"Status: Door failed to lock by RF [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("lockRFFailed",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "09"):
					indigo.server.log(u"Status: Door re-locked automatically [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("relockedAuto",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Locked")
				elif (bytes[14] == "0A"):
					indigo.server.log(u"Status: Door failed to relock automatically [Node: %s]" % int(bytes[5],16))
					self.updateState(int(bytes[5],16),"lockState","Unlocked")
				elif (bytes[14] == "0B"):
					indigo.server.log(u"Status: Door lock jammed [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("deadboltJammed",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Jammed")
				elif (bytes[14] == "0C"):
					indigo.server.log(u"Status: All codes deleted [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "0D"):
					indigo.server.log(u"Status: User code deleted [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "0E"):
					indigo.server.log(u"Status: New user code added [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "0F"):
					indigo.server.log(u"Status: Updating user failed - PIN already exists [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "10"):
					indigo.server.log(u"Status: Keypad temporarily disabled [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "11"):
					indigo.server.log(u"Status: Keypad in use [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "12"):
					indigo.server.log(u"Status: Master Code updated [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "13"):
					indigo.server.log(u"Status: Invalid code limit exceeded [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("invalidLimit",int(bytes[5],16),"")
				elif (bytes[14] == "14"):
					indigo.server.log(u"Status: Invalid user code entered when unlocking door [Node: %s]" % int(bytes[5],16))
					self.triggerInvalidCode(int(bytes[5],16),"")
				elif (bytes[14] == "15"):
					indigo.server.log(u"Status: Invalid user code entered when locking door [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "16"):
					indigo.server.log(u"Status: Door is open [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("doorOpened",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Open")
				elif (bytes[14] == "17"):
					indigo.server.log(u"Status: Door is closed [Node: %s]" % int(bytes[5],16))
					self.triggerEvent("doorClosed",int(bytes[5],16),"")
					self.updateState(int(bytes[5],16),"lockState","Closed")
			elif (bytes[13] == "07"):
				if (bytes[14] == "01"):
					indigo.server.log(u"Status: Previous alarm/event cleared [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "02"):
					indigo.server.log(u"Status: Intrusion alert [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "03"):
					indigo.server.log(u"Status: Intrusion alert [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "04"):
					indigo.server.log(u"Status: Lock tamper switch activated [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "05"):
					indigo.server.log(u"Status: Attempted tamper: invalid code entered %s [Node: %s]" % (int(bytes[16],16),int(bytes[5],16)))
					self.triggerEvent("lockedByCode",int(bytes[5],16),int(bytes[16],16))
				elif (bytes[14] == "09"):
					indigo.server.log(u"Status: Tamper alert: lock motion detected [Node: %s]" % int(bytes[5],16))
				elif (bytes[14] == "FE"):
					indigo.server.log(u"Status: Unknown alarm event [Node: %s]" % int(bytes[5],16))

		if (bytes[7] == "63") and (bytes[8] == "03"): #COMMAND_CLASS_USER_CODE = User Code status
			self.debugLog(u"-----")
			self.debugLog(u"User Code Status received:")
			self.debugLog(u"Raw command: %s" % (byteListStr))
			self.debugLog(u"Node:  %s" % (int(bytes[5],16)))
			self.debugLog(u"User:  %s" % (int(bytes[9],16)))
			if (bytes[10] == "01"): #Code is set/slot is occupied
				if len(bytes) < 22: # Code with characters
					retCode = ' '.join([chr(int(bytex, 16)) for bytex in bytes[11:len(bytes)-1]])
				else: # Pin or RFID tag
					retCode = ' '.join(bytes[11:len(bytes)-1])
				indigo.server.log(u"Status:  User code %s is %s [Node: %s]" % (int(bytes[9],16), retCode, int(bytes[5],16)))
			else:
				indigo.server.log(u"Status:  User code %s is blank [Node: %s]" % (int(bytes[9],16),int(bytes[5],16)))
			self.debugLog(u"-----")

		if (bytes[7] == "62") and (bytes[8] == "03"): #COMMAND_CLASS_DOOR = Door Lock Status
			#self.debugLog(u"-----")
			#self.debugLog(u"Lock Status Report received:")
			self.debugLog(u"Door: %s" % (byteListStr))
			self.debugLog("")
			self.debugLog(u"Node:  %s" % (int(bytes[5],16)))
			self.debugLog(u"Type:  %s" % (int(bytes[9],16)))
			self.debugLog(u"User:  %s" % (int(bytes[10],16)))
			if (bytes[9] == "00"):
				indigo.server.log(u"Status: Door is unlocked [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "01"):
				indigo.server.log(u"Status: Door is unlocked: auto relock active [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "10"):
				indigo.server.log(u"Status: Door is unlocked on the inside [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "11"):
				indigo.server.log(u"Status: Door is unlocked on the inside: auto relock active [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "20"):
				indigo.server.log(u"Status: Door is unlocked on the outside [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "21"):
				indigo.server.log(u"Status: Door is unlocked on the outside: auto relock active [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unlocked")
			elif (bytes[9] == "FE"):
				indigo.server.log(u"Status: Door lock state unknown [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Unknown")
			elif (bytes[9] == "FF"):
				indigo.server.log(u"Status: Door is locked [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"lockState","Locked")
			if (bytes[11] == "00"): #Latch, Bold, Door status by binary bitmask
				indigo.server.log(u"Latch open, Bolt locked, Door open [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "01"):
				indigo.server.log(u"Latch open, Bolt locked, Door closed [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "02"):
				indigo.server.log(u"Latch open, Bolt unlocked, Door open [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "03"):
				indigo.server.log(u"Latch open, Bolt unlocked, Door closed [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "04"):
				indigo.server.log(u"Latch closed, Bolt locked, Door open [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "05"):
				indigo.server.log(u"Latch closed, Bolt locked, Door closed [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")
			elif (bytes[11] == "06"):
				indigo.server.log(u"Latch closed, Bolt unlocked, Door open [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Open")
			elif (bytes[11] == "07"):
				indigo.server.log(u"Latch closed, Bolt unlocked, Door closed [Node: %s]" % (int(bytes[5],16)))
				self.updateState(int(bytes[5],16),"handleState","Closed")


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
		self.debugLog(u"lockIDs: %s" % (str(self.lockIDs)))


########################################
	def triggerStartProcessing(self, trigger):
		self.debugLog(u"Start processing trigger " + unicode(trigger.name))
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
		self.debugLog(u"Stop processing trigger " + unicode(trigger.name))
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
			if (userNo <> ""):
				dUserNo = self.events[eventType][trigger].pluginProps["userNo"]
			else:
				dUserNo = "" #We pass in "" as userNo if the trigger doesn't require a userNo match.  We then match "" to "" below.
			self.debugLog(u"---")
			self.debugLog(u"dNodeID:   #%s#" % (dNodeID))
			self.debugLog(u"eventNode: #%s#" % (eventNode))
			self.debugLog(u"dUserNo:   #%s#" % (str(dUserNo)))
			self.debugLog(u"userNo:    #%s#" % (str(userNo)))
			if (str(eventNode) == str(dNodeID)):
				if ((str(dUserNo) == "Any") or (str(dUserNo) == str(userNo))):
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
			self.debugLog(u"dNodeID:   #%s#" % (dNodeID))
			self.debugLog(u"eventNode: #%s#" % (eventNode))
			self.debugLog(u"dCode:   #%s#" % (str(dCode)))
			self.debugLog(u"inCode:    #%s#" % (str(inCode)))
			if (str(eventNode) == str(dNodeID)):
				if ((str(dCodeNo) == "") or (str(dCode) == str(inCode))):
					indigo.trigger.execute(trigger)
					self.debugLog(u"Executing trigger")

	def setPin(self,userNo,userPin,indigoDev):
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Setting PIN for user " + str(userNo) + " to: " + str(userPin))

		codeStr = [99, 01, int(userNo), 01] + self.getPinStr(userPin)

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def clearPin(self,userNo,indigoDev):
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Clearing PIN for user " + userNo)

		codeStr = [99, 01, int(userNo), 00]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)

	def getPin(self,userNo,indigoDev):
		self.debugLog(str(self.nodeFromDev))
		node = self.nodeFromDev[int(indigoDev)]
		self.debugLog("Node: " + str(node))
		indigo.server.log("Requesting PIN for user " + userNo)

		codeStr = [99, 02, int(userNo)]

		indigo.zwave.sendRaw(device=indigo.devices[self.zedFromDev[indigoDev]],cmdBytes=codeStr,sendMode=1)


	def updateState(self, nodeID, state, newState):
		self.debugLog(u"Updating state: " + unicode(state))
		dev=indigo.devices[self.devFromNode[nodeID]]
		dev.updateStateOnServer(state, newState)


