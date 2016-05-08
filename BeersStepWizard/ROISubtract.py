""" This is Step 1. The user selects the pre- and post-contrast volumes 
	from which to construct a substraction map. 
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

""" VolumeSelectStep inherits from BeersSingleStep, with itself inherits
	from a ctk workflow class. 
"""

class ROISubtractStep(BeersSingleStep) :

	def __init__(self, stepid):

		""" This method creates a drop-down menu that includes the whole step.
			The description also acts as a tooltip for the button. There may be 
			some way to override this. The initialize method is presumably inherited
			from ctk.
		"""

		self.initialize( stepid )
		self.setName( '4. Volume Selection' )
		self.setDescription( 'Select the pre- and post-contrast volumes to calculate the subtraction map.' )

		self.__parent = super(ROISubtractStep, self)

	def createUserInterface(self):

		""" This method uses qt to create a user interface. qMRMLNodeComboBox
			is a drop down menu for picking MRML files. MRML files are collected in
			a scene, hence .setMRMLscene. Test data currently not functional for
			some reason.
		"""

		self.__layout = self.__parent.createUserInterface()
	 
		baselineScanLabel = qt.QLabel( 'Pre-contrast scan:' )
		self.__baselineVolumeSelector = slicer.qMRMLNodeComboBox()
		self.__baselineVolumeSelector.toolTip = "Choose the pre-contrast scan"
		self.__baselineVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
		self.__baselineVolumeSelector.setMRMLScene(slicer.mrmlScene)
		self.__baselineVolumeSelector.addEnabled = 0

		followupScanLabel = qt.QLabel( 'Post-contrast scan:' )
		self.__followupVolumeSelector = slicer.qMRMLNodeComboBox()
		self.__followupVolumeSelector.toolTip = "Choose the post-contrast scan"
		self.__followupVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
		self.__followupVolumeSelector.setMRMLScene(slicer.mrmlScene)
		self.__followupVolumeSelector.addEnabled = 0

		self.__layout.addRow( baselineScanLabel, self.__baselineVolumeSelector )
		self.__layout.addRow( followupScanLabel, self.__followupVolumeSelector )

		qt.QTimer.singleShot(0, self.killButton)

	def killButton(self):

		# ctk creates a useless final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='ROISubtractStep')
		if len(bl):
			bl[0].hide()

	def validate( self, desiredBranchId ):

		# validate is called whenever go to a different step
		self.__parent.validate( desiredBranchId )

	def onEntry(self, comingFrom, transitionType):

		super(ROISubtractStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)

		# A different attempt to get rid of the extra workflow button.
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 