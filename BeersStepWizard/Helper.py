""" This is a helper file loaded by individual steps in the module. It has
	been copied from ChangeTracker at https://github.com/fedorov/ChangeTrackerPy.
	Not all methods are used.
"""

from __main__ import vtk, slicer

import sys
import time

class Helper( object ):

	@staticmethod
	def Error( message ):

		print "[ChangeTrackerPy " + time.strftime( "%m/%d/%Y %H:%M:%S" ) + "]: ERROR: " + str( message )
		sys.stdout.flush()

	@staticmethod
	def ErrorPopup( message ):

		messageBox = qt.QMessageBox()
		messageBox.critical(None,'',message)

	@staticmethod
	def Debug( message ):

		showDebugOutput = 0
		from time import strftime
		if showDebugOutput:
			print "[ChangeTrackerPy " + time.strftime( "%m/%d/%Y %H:%M:%S" ) + "] DEBUG: " + str( message )
			sys.stdout.flush()

	@staticmethod
	def CreateSpace( n ):

		spacer = ""
		for s in range( n ):
			spacer += " "

		return spacer

	@staticmethod
	def GetNthStepId( n ):

		steps = [None, # 0
				 'SelectScans', # 1
				 'DefineROI', # 2
				 'SegmentROI', # 3
				 'AnalyzeROI', # 4
				 'ReportROI', # 5
				 ]                        

		if n < 0 or n > len( steps ):
			n = 0

		return steps[n]

	@staticmethod
	def SetBgFgVolumes(bg, fg):
		appLogic = slicer.app.applicationLogic()
		selectionNode = appLogic.GetSelectionNode()
		selectionNode.SetReferenceActiveVolumeID(bg)
		selectionNode.SetReferenceSecondaryVolumeID(fg)
		appLogic.PropagateVolumeSelection()

	@staticmethod
	def SetLabelVolume(lb):
		appLogic = slicer.app.applicationLogic()
		selectionNode = appLogic.GetSelectionNode()
		selectionNode.SetReferenceActiveLabelVolumeID(lb)
		appLogic.PropagateVolumeSelection()

	@staticmethod
	def InitVRDisplayNode(vrDisplayNode, volumeID, roiID):
		vrLogic = slicer.modules.volumerendering.logic()

		print('ChangeTracker VR: will observe ID '+volumeID)
		propNode = vrDisplayNode.GetVolumePropertyNode()

		if propNode == None:
			propNode = slicer.vtkMRMLVolumePropertyNode()
			slicer.mrmlScene.AddNode(propNode)
		else:
			print('Property node: '+propNode.GetID())

		vrDisplayNode.SetAndObserveVolumePropertyNodeID(propNode.GetID())

		vrDisplayNode.SetAndObserveROINodeID(roiID)

		vrDisplayNode.SetAndObserveVolumeNodeID(volumeID)

		vrLogic.CopyDisplayToVolumeRenderingDisplayNode(vrDisplayNode)

	@staticmethod
	def findChildren(widget=None,name="",text=""):

		if not widget:
			widget = mainWindow()
		children = []
		parents = [widget]
		while parents != []:
			p = parents.pop()
			parents += p.children()
			if name and p.name.find(name)>=0:
				children.append(p)
			elif text: 
				try:
					p.text
					if p.text.find(text)>=0:
						children.append(p)
				except AttributeError:
			  		pass
		return children

	@staticmethod
	def getNodeByID(id):
		return slicer.mrmlScene.GetNodeByID(id)

	@staticmethod
	def readFileAsString(fname):
		s = ''
		with open(fname, 'r') as f:
			s = f.read()
		return s
