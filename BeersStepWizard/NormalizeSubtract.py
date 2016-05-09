""" This is Step 4. The user has the option to normalize intensity values
	across pre- and post-contrast images.
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

""" NormalizeSubtractStep inherits from BeersSingleStep, with itself inherits
	from a ctk workflow class. 
"""

class NormalizeSubtractStep( BeersSingleStep ) :

	def __init__( self, stepid ):

		""" This method creates a drop-down menu that includes the whole step.
			The description also acts as a tooltip for the button. There may be 
			some way to override this. The initialize method is presumably inherited
			from ctk.
		"""

		self.initialize( stepid )
		self.setName( '4. Normalization and Subtraction' )
		self.setDescription( 'You may want to normalize the intensities between your pre and post-contrast images before subtracting them. This may lead to better contrast in the resulting image. The method below divides both images by the standard deviation of their intensities in order to get a measure of relative intensity. ' )

		self.__status = 'uncalled'
		self.__parent = super( NormalizeSubtractStep, self )

	def createUserInterface( self ):

		""" As of now, this step's UI is fairly simple. If there are other methods of
			normalization, they could be added here.
		"""

		self.__layout = self.__parent.createUserInterface()

		self.NormSubtractFrame = qt.QFrame()
		self.NormSubtractFrame.setLayout(qt.QHBoxLayout())
		self.__layout.addWidget(self.NormSubtractFrame)


		self.__normalizationButton = qt.QPushButton('Run Gaussian Normalization')
		self.NormSubtractFrame.layout().addWidget(self.__normalizationButton)

		self.__subtractionButton = qt.QPushButton('Run Contrast Subtraction')
		self.NormSubtractFrame.layout().addWidget(self.__subtractionButton)

		self.__normalizationButton.connect('clicked()', self.onNormalizationRequest)
		self.__subtractionButton.connect('clicked()', self.onSubtractionRequest)


	def killButton(self):
		# ctk creates a useless final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='NormalizeSubtractStep')
		if len(bl):
			bl[0].hide()

	def validate( self, desiredBranchId ):

		if self.__status != 'Completed':
			self.__parent.validationFailed(desiredBranchId, 'Error','You must have completed an image subtraction before moving to the next step.')
		else:
			self.__parent.validationSucceeded(desiredBranchId)

	def onEntry(self, comingFrom, transitionType):
		print "Entering normalization step."
		super(NormalizeSubtractStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)
		
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):
		self.ROIPrep() 
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def ROIPrep(self):
		pNode = self.parameterNode()

		subtractVolume = Helper.getNodeByID(pNode.GetParameter('subtractVolumeID'))
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

	def onSubtractionRequest(self):

		pNode = self.parameterNode()
		baselineVolumeID = pNode.GetParameter('baselineVolumeID')
		followupVolumeID = pNode.GetParameter('followupVolumeID')

		subtractVolume = slicer.vtkMRMLScalarVolumeNode()
		subtractVolume.SetScene(slicer.mrmlScene)
		subtractVolume.SetName('Post Subtraction Node')
		slicer.mrmlScene.AddNode(subtractVolume)
		pNode.SetParameter('subtractVolumeID', subtractVolume.GetID())

		parameters = {}
		parameters["inputVolume1"] = baselineVolumeID
		parameters["inputVolume2"] = followupVolumeID
		parameters['outputVolume'] = subtractVolume.GetID()
		parameters['order'] = '1'

		self.__cliNode = None
		self.__cliNode = slicer.cli.run(slicer.modules.subtractscalarvolumes, self.__cliNode, parameters)

		# An event listener for the CLI. To-Do: Add a progress bar.
		self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processSubtractionCompletion)
		self.__subtractionButton.setText('Subtraction running...')
		self.__subtractionButton.setEnabled(0)


	def processSubtractionCompletion(self, node, event):

		""" This updates the registration button with the CLI module's convenient status
			indicator. Upon completion, it applies the transform to the followup node.
			Furthermore, it sets the followup node to be the baseline node in the viewer.
			It also saves the transform for later in the parameter node.
		"""

		self.__status = node.GetStatusString()
		# self.__registrationStatus.setText('Registration ' + self.__status)
		print self.__status

		if self.__status == 'Completed':
			# self.__registrationButton.setEnabled(1)
			self.__subtractionButton.setText('Subtraction completed!')

			# pNode = self.parameterNode()
			# followupNode = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
			# followupNode.SetAndObserveTransformNodeID(self.__followupTransform.GetID())
		
			# Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

			# pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())

	def onNormalizationRequest(self):

		""" This method uses vtk algorithms to perform simple image calculations. Slicer 
			images are stored in vtkImageData format, making it difficult to edit them
			without using vtk. Here, vtkImageShiftScale and vtkImageHistogramStatistics
			are used to generate max, standard deviation, and simple multiplication. Currently,
			I create an instance for both baseline and followup; a better understanding
			of vtk may lead me to consolidate them into one instance later.

		"""

		print "Normalization Called"
		self.__normalizationButton.setEnabled(0)
		self.__normalizationButton.setText('Normalization running...')

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
		self.__normalizationButton.setText('Normalization complete!')

		# tests used to check post-transofrm pixel values
		# a = slicer.util.array(baselineLabel)
		# c = slicer.util.array(followupLabel)
		# print a[100,190,:]
		# print b[100,190,:]
		# print c[100,190,:]
		# print d[100,190,:]
