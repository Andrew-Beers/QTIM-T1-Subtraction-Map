from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *
import numpy as np
from vtk.util import numpy_support

class NormalizationStep( BeersSingleStep ) :

	def __init__( self, stepid ):

		""" This method creates a drop-down menu that includes the whole step.
		The description also acts as a tooltip for the button. There may be 
		some way to override this. The initialize method is presumably inherited
		from ctk.
		"""

		self.initialize( stepid )
		self.setName( '3. Normalization' )
		self.setDescription( 'If so desired, normalize your images by dividing them by their standard deviations.' )

		self.__parent = super( NormalizationStep, self )

	def createUserInterface( self ):

		""" As of now, this step's UI is fairly simple. If there are other methods of
			normalization, they could be added here.
		"""

		self.__layout = self.__parent.createUserInterface()

		self.__normalizationButton = qt.QPushButton('Run Gaussian Normalization')

		self.__layout.addRow(self.__normalizationButton)

		self.__normalizationButton.connect('clicked()', self.onNormalizationRequest)


	def killButton(self):
		# ctk creates a useless final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='NormalizationStep')
		if len(bl):
			bl[0].hide()

	def validate( self, desiredBranchId ):

		# For now, no validation required.
		self.__parent.validate( desiredBranchId )

	def onEntry(self, comingFrom, transitionType):

		super(NormalizationStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)
		
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		# extra error checking, in case the user manages to click ReportROI button

		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def onNormalizationRequest(self):

		""" This method uses vtk algorithms to perform simple image calculations. Slicer 
			images are stored in vtkImageData format, making it difficult to edit them
			without using vtk. Here, vtkImageShiftScale and vtkImageHistogramStatistics
			are used to generate max, standard deviation, and simple multiplication. Currently,
			I create an instance for both baseline and followup; a better understanding
			of vtk may lead me to consolidate them into one instance later.

		"""

		pNode = self.parameterNode()

		baselineLabel = pNode.GetParameter('baselineVolumeID')
		followupLabel = pNode.GetParameter('followupVolumeID')

		baselineNode = slicer.mrmlScene.GetNodeByID(baselineLabel)
		followupNode = slicer.mrmlScene.GetNodeByID(followupLabel)

		baselineImage = baselineNode.GetImageData()
		followupImage = followupNode.GetImageData()

		# tests used to check pre-transform pixel values
		# b = slicer.util.array(baselineLabel)
		# d = slicer.util.array(followupLabel)

		imageArray = [baselineImage, followupImage]
		stdArray = [0,0]
		maxArray = [0,0]
		vtkScaleArray = [vtk.vtkImageShiftScale(), vtk.vtkImageShiftScale()]
		vtkStatsArray = [vtk.vtkImageHistogramStatistics(), vtk.vtkImageHistogramStatistics()]

		# descriptive statistics are retrieved
		for i in [0,1]:
			vtkStatsArray[i].SetInputData(imageArray[i])
			vtkStatsArray[i].Update()
			maxArray[i] = vtkStatsArray[i].GetMaximum()
			stdArray[i] = vtkStatsArray[i].GetStandardDeviation()

		# values are rescaled to more intense image.
		CommonMax = maxArray.index(max(maxArray))

		# image calculations are performed
		for i in [0,1]:
			vtkScaleArray[i].SetInputData(imageArray[i])
			vtkScaleArray[i].SetOutputScalarTypeToInt()
			scalar = float(stdArray[CommonMax]) / float(stdArray[i])
			vtkScaleArray[i].SetScale(scalar)
			vtkScaleArray[i].Update()
			imageArray[i] = vtkScaleArray[i].GetOutput()

		# node image data is replaced. One of the images will not effectively change.
		baselineNode.SetAndObserveImageData(imageArray[0])
		followupNode.SetAndObserveImageData(imageArray[1])

		# tests used to check post-transofrm pixel values
		# a = slicer.util.array(baselineLabel)
		# c = slicer.util.array(followupLabel)
		# print a[100,190,:]
		# print b[100,190,:]
		# print c[100,190,:]
		# print d[100,190,:]
