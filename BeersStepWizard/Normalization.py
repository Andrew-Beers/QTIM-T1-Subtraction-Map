""" This is Step 3. The user has the option to normalize intensity values
	across pre- and post-contrast images.
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

""" NormalizationStep inherits from BeersSingleStep, with itself inherits
	from a ctk workflow class. 
"""

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
		print "validating normalization..."
		# For now, no validation required.
		self.__parent.validationSucceeded(desiredBranchId)

	def onEntry(self, comingFrom, transitionType):
		print "Entering normalization step."
		super(NormalizationStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)
		
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		self.ROIPrep()
		# extra error checking, in case the user manages to click ReportROI button
		print "Leaving normalization step."
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def ROIPrep(self):
		pNode = self.parameterNode()

		baselineVolume = Helper.getNodeByID(pNode.GetParameter('baselineVolumeID'))
		roiTransformID = pNode.GetParameter('roiTransformID')
		roiTransformNode = None

		if roiTransformID != '':
			roiTransformNode = Helper.getNodeByID(roiTransformID)
		else:
			roiTransformNode = slicer.vtkMRMLLinearTransformNode()
			slicer.mrmlScene.AddNode(roiTransformNode)
			pNode.SetParameter('roiTransformID', roiTransformNode.GetID())

		dm = vtk.vtkMatrix4x4()
		# baselineVolume.GetIJKToRASDirectionMatrix(dm)
		dm.SetElement(0,3,0)
		dm.SetElement(1,3,0)
		dm.SetElement(2,3,0)
		dm.SetElement(0,0,abs(dm.GetElement(0,0)))
		dm.SetElement(1,1,abs(dm.GetElement(1,1)))
		dm.SetElement(2,2,abs(dm.GetElement(2,2)))
		roiTransformNode.SetAndObserveMatrixTransformToParent(dm)

	def onNormalizationRequest(self):

		""" This method uses vtk algorithms to perform simple image calculations. Slicer 
			images are stored in vtkImageData format, making it difficult to edit them
			without using vtk. Here, vtkImageShiftScale and vtkImageHistogramStatistics
			are used to generate max, standard deviation, and simple multiplication. Currently,
			I create an instance for both baseline and followup; a better understanding
			of vtk may lead me to consolidate them into one instance later.

		"""

		print "Normalization Called"

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
