""" This is Step 5. The user has the option to normalize intensity values
	across pre- and post-contrast images.
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

import string

""" ThresholdStep inherits from BeersSingleStep, with itself inherits
	from a ctk workflow class. 
"""

class ThresholdStep( BeersSingleStep ) :

	def __init__( self, stepid ):

		""" This method creates a drop-down menu that includes the whole step.
			The description also acts as a tooltip for the button. There may be 
			some way to override this. The initialize method is presumably inherited
			from ctk.
		"""

		self.initialize( stepid )
		self.setName( '5. Threshold' )
		self.setDescription( 'Highlight the portion of your ROI you would like to see annotated in the final step.' )

		self.__vrDisplayNode = None
		self.__threshold = [ -1, -1 ]
		
		# initialize VR stuff
		self.__vrLogic = slicer.modules.volumerendering.logic()
		self.__vrOpacityMap = None

		self.__roiSegmentationNode = None
		self.__roiVolume = None

		self.__parent = super( ThresholdStep, self )

	def createUserInterface( self ):

		""" As of now, this step's UI is fairly simple. If there are other methods of
			normalization, they could be added here.
		"""

		self.__layout = self.__parent.createUserInterface()

		threshLabel = qt.QLabel('Choose threshold:')
		self.__threshRange = slicer.qMRMLRangeWidget()
		self.__threshRange.decimals = 0
		self.__threshRange.singleStep = 1

		self.__layout.addRow(threshLabel, self.__threshRange)
		self.__threshRange.connect('valuesChanged(double,double)', self.onThresholdChanged)
		qt.QTimer.singleShot(0, self.killButton)

	def onThresholdChanged(self): 
	
		if self.__vrOpacityMap == None:
			return
		
		range0 = self.__threshRange.minimumValue
		range1 = self.__threshRange.maximumValue

		self.__vrOpacityMap.RemoveAllPoints()
		self.__vrOpacityMap.AddPoint(0,0)
		self.__vrOpacityMap.AddPoint(0,0)
		self.__vrOpacityMap.AddPoint(range0-1,0)
		self.__vrOpacityMap.AddPoint(range0,1)
		self.__vrOpacityMap.AddPoint(range1,1)
		self.__vrOpacityMap.AddPoint(range1+1,0)

		# update the label volume accordingly
		thresh = vtk.vtkImageThreshold()
		if vtk.VTK_MAJOR_VERSION <= 5:
			thresh.SetInput(self.__roiVolume.GetImageData())
		else:
			thresh.SetInputData(self.__roiVolume.GetImageData())
		thresh.ThresholdBetween(range0, range1)
		thresh.SetInValue(10)
		thresh.SetOutValue(0)
		thresh.ReplaceOutOn()
		thresh.ReplaceInOn()
		thresh.Update()

		self.__roiSegmentationNode.SetAndObserveImageData(thresh.GetOutput())

	def killButton(self):
		# ctk creates a useless final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='ThresholdStep')
		if len(bl):
			bl[0].hide()

	def validate( self, desiredBranchId ):
		# For now, no validation required.
		self.__parent.validationSucceeded(desiredBranchId)

	def onEntry(self, comingFrom, transitionType):
		super(ThresholdStep, self).onEntry(comingFrom, transitionType)

		pNode = self.parameterNode()
		self.updateWidgetFromParameters(pNode)

		Helper.SetBgFgVolumes(pNode.GetParameter('croppedSubtractVolumeID'),'')

		# TODO: initialize volume selectors, fit ROI to slice viewers, create
		# label volume, initialize the threshold, initialize volume rendering ?

		roiVolume = Helper.getNodeByID(pNode.GetParameter('croppedSubtractVolumeID'))
		self.__roiVolume = roiVolume
		self.__roiSegmentationNode = Helper.getNodeByID(pNode.GetParameter('croppedSubtractVolumeSegmentationID'))
		vrDisplayNodeID = pNode.GetParameter('vrDisplayNodeID')

		if self.__vrDisplayNode == None:
			if vrDisplayNodeID != '':
				self.__vrDisplayNode = slicer.mrmlScene.GetNodeByID(vrDisplayNodeID)

		if self.__useThresholds:

		  roiNodeID = pNode.GetParameter('roiNodeID')
		  if roiNodeID == None:
			Helper.Error('Failed to find ROI node -- it should have been defined in the previous step!')
			return

		  Helper.InitVRDisplayNode(self.__vrDisplayNode, roiVolume.GetID(), roiNodeID)

		  self.__vrOpacityMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
		  vrColorMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
		
		# setup color transfer function once
		
		subtractROIVolume = Helper.getNodeByID(pNode.GetParameter('croppedSubtractVolumeID'))
		subtractROIRange = subtractROIVolume.GetImageData().GetScalarRange()

		vrColorMap.RemoveAllPoints()
		vrColorMap.AddRGBPoint(0, 0, 0, 0) 
		vrColorMap.AddRGBPoint(subtractROIRange[0]-1, 0, 0, 0) 
		vrColorMap.AddRGBPoint(subtractROIRange[0], 0.8, 0, 0) 
		vrColorMap.AddRGBPoint(subtractROIRange[1], 0.8, 0.8, 0) 
		vrColorMap.AddRGBPoint(subtractROIRange[1]+1, 0, 0, 0) 

		self.__vrDisplayNode.VisibilityOn()

		threshRange = [self.__threshRange.minimumValue, self.__threshRange.maximumValue]
		self.__vrOpacityMap.RemoveAllPoints()
		self.__vrOpacityMap.AddPoint(0,0)
		self.__vrOpacityMap.AddPoint(0,0)
		self.__vrOpacityMap.AddPoint(threshRange[0]-1,0)
		self.__vrOpacityMap.AddPoint(threshRange[0],1)
		self.__vrOpacityMap.AddPoint(threshRange[1],1)
		self.__vrOpacityMap.AddPoint(threshRange[1]+1,0)

		labelsColorNode = slicer.modules.colors.logic().GetColorTableNodeID(9)
		self.__roiSegmentationNode.GetDisplayNode().SetAndObserveColorNodeID(labelsColorNode)

		Helper.SetLabelVolume(self.__roiSegmentationNode.GetID())

		self.onThresholdChanged()
		
		pNode.SetParameter('currentStep', self.stepid)
	
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		# extra error checking, in case the user manages to click ReportROI button
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def updateWidgetFromParameters(self, pNode):
  
		subtractROIVolume = Helper.getNodeByID(pNode.GetParameter('croppedSubtractVolumeID'))
		subtractROIRange = subtractROIVolume.GetImageData().GetScalarRange()
		self.__threshRange.minimum = subtractROIRange[0]
		self.__threshRange.maximum = subtractROIRange[1]

		if pNode.GetParameter('useSegmentationThresholds') == 'True':
			self.__useThresholds = True

			thresholdRange = pNode.GetParameter('thresholdRange')
			if thresholdRange != '':
				rangeArray = string.split(thresholdRange, ',')
				self.__threshRange.minimumValue = float(rangeArray[0])
				self.__threshRange.maximumValue = float(rangeArray[1])
			else:
				Helper.Error('Unexpected parameter values! Error code CT-S03-TNA. Please report')
		else:
		  self.__useThresholds = False

		segmentationID = pNode.GetParameter('croppedSubtractVolumeSegmentationID')
		self.__roiSegmentationNode = Helper.getNodeByID(segmentationID)

