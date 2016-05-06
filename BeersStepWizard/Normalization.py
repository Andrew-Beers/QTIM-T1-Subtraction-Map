from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *
import numpy as np
from vtk.util import numpy_support

class NormalizationStep( BeersSingleStep ) :

	def __init__( self, stepid ):
		self.initialize( stepid )
		self.setName( '3. Normalization' )
		self.setDescription( 'Choose a normalization method. Choose the Skip Normalization option to continue.' )

		self.__parent = super( NormalizationStep, self )

	def createUserInterface( self ):
		'''
		'''
		self.__layout = self.__parent.createUserInterface()

		self.__normalizationButton = qt.QPushButton('Run Gaussian Normalization')

		self.__layout.addRow(self.__normalizationButton)

		self.__normalizationButton.connect('clicked()', self.onNormalizationRequest)


	def killButton(self):
		# hide useless button
		bl = slicer.util.findChildren(text='NormalizationStep')
		if len(bl):
			bl[0].hide()

	def validate( self, desiredBranchId ):
		'''
		'''
		self.__parent.validationSucceeded(desiredBranchId)

	def onEntry(self, comingFrom, transitionType):

		super(NormalizationStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)
		
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		# extra error checking, in case the user manages to click ReportROI button

		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def onNormalizationRequest(self):
		pNode = self.parameterNode()

		baselineLabel = pNode.GetParameter('baselineVolumeID')
		followupLabel = pNode.GetParameter('followupVolumeID')

		baselineNode = slicer.util.getNode(baselineLabel)
		followupNode = slicer.util.getNode(followupLabel)

		baselineImage = baselineNode.GetImageData()
		followupImage = followupNode.GetImageData()

		imageArray = [baselineImage, followupImage]
		b = slicer.util.array(baselineLabel)
		d = slicer.util.array(followupLabel)
		stdArray = [0,0]
		maxArray = [0,0]
		vtkScaleArray = [vtk.vtkImageShiftScale(), vtk.vtkImageShiftScale()]
		vtkStatsArray = [vtk.vtkImageHistogramStatistics(), vtk.vtkImageHistogramStatistics()]
		# print vtkScaleArray

		for i in [0,1]:
			vtkStatsArray[i].SetInputData(imageArray[i])
			vtkStatsArray[i].Update()
			maxArray[i] = vtkStatsArray[i].GetMaximum()
			stdArray[i] = vtkStatsArray[i].GetStandardDeviation()
			# print maxArray
			# print stdArray

		PreMax = maxArray.index(max(maxArray))

		for i in [0,1]:
			vtkScaleArray[i].SetInputData(imageArray[i])
			vtkScaleArray[i].SetOutputScalarTypeToInt()
			scalar = float(stdArray[PreMax]) / float(stdArray[i])
			vtkScaleArray[i].SetScale(scalar)
			vtkScaleArray[i].Update()
			imageArray[i] = vtkScaleArray[i].GetOutput()

		baselineNode.SetAndObserveImageData(imageArray[0])
		followupNode.SetAndObserveImageData(imageArray[1])

		a = slicer.util.array(baselineLabel)
		c = slicer.util.array(followupLabel)
		print a[100,190,:]
		print b[100,190,:]
		print c[100,190,:]
		print d[100,190,:]

		# baselineNode = slicer.util.getNode(baselineLabel)
		# followupNode = slicer.util.getNode(followupLabel)
		# print baselineNode

		# baselineImage = baselineNode.GetImageData()
		# followupImage = followupNode.GetImageData()

		# imageArray = [baselineImage, followupImage]
		# stdArray = [0,0]
		# maxArray = [0,0]
		# stdMaxArray = [0,0]
		# stdImageArray = [vtk.vtkImageData(),vtk.vtkImageData()]
		# normImageArray = [vtk.vtkImageData(),vtk.vtkImageData()]

		# vtkScale = vtk.vtkImageShiftScale()
		# vtkScale.SetOutputScalarTypeToFloat()
		# vtkStats = vtk.vtkImageHistogramStatistics()

		# for i in [0,1]:
		# 	vtkStats.SetInputData(imageArray[i])
		# 	vtkStats.Update()
		# 	maxArray[i] = vtkStats.GetMaximum()
		# 	stdArray[i] = vtkStats.GetStandardDeviation()
		# 	vtkScale.SetInputData(imageArray[i])
		# 	vtkScale.Update()
		# 	vtkScale.SetOutputScalarTypeToFloat()
		# 	vtkScale.SetScale(1 / stdArray[i])
		# 	stdImageArray[i] = vtkScale.GetOutput()
		# 	vtkStats.SetInputData(stdImageArray[i])
		# 	vtkStats.Update()
		# 	stdMaxArray[i] = vtkStats.GetMaximum()
		# 	print maxArray[i]
		# 	print stdMaxArray[i]

		# PreMax = max(maxArray)
		# PostMax = max(stdMaxArray)

		# for i in [0,1]:
		# 	vtkScale.SetInputData(stdImageArray[i])
		# 	vtkScale.Update()
		# 	vtkScale.OutputScalarTypeToInt()
		# 	vtkScale.SetScale(PreMax / PostMax)
		# 	normImageArray[i] = vtkScale.GetOutput()

		# # baselineArray = slicer.util.array(baselineLabel)
		# # followupArray = slicer.util.array(followupLabel)
		# # print baselineArray[100,190,:]
		# # print baselineArray.dtype

		# # MaxIntensity = max(baselineArray.max(), followupArray.max())
		# # print MaxIntensity

		# # MinIntensity = min(baselineArray.min(), followupArray.min())
		# # print MinIntensity

		# if MinIntensity < 0:
		# 	print "Negative Values!"

		# baselineMultiplier = 0.5
		# vtkMultiply.setInput1Data(baselineNode.GetImageData())
		# vtkMultiply.setConstantK(baselineMultiplier)

		# baselineArray = baselineArray / baselineArray.std()
		# followupArray = followupArray / followupArray.std()
		# print baselineArray[100,190,:]

		# MaxRelativeIntensity = max(baselineArray.max(), followupArray.max())

		# baselineArray = baselineArray * (MaxIntensity / MaxRelativeIntensity) / 2
		# followupArray = followupArray * (MaxIntensity / MaxRelativeIntensity) / 2
		# print baselineArray[100,190,:]

		# baselineArray = np.around(baselineArray)
		# followupArray = np.around(followupArray)
		# print baselineArray[100,190,:]
		# print baselineArray.dtype

		# # baselineArray = baselineArray - 300

		# baselineArray = baselineArray.astype('int16')
		# followupArray = followupArray.astype('int16')
		# print baselineArray.dtype
		# print baselineArray[100,190,:]

		# ijkToRAS = vtk.vtkMatrix4x4()
		# baselineNode.GetIJKToRASMatrix(ijkToRAS)
		# print 'Coordinates Received'

		# VTK_baseline = numpy_support.numpy_to_vtk(num_array=baselineArray.ravel(), deep=True, array_type=vtk.VTK_INT)
		# VTK_followup = numpy_support.numpy_to_vtk(num_array=baselineArray.ravel(), deep=True, array_type=vtk.VTK_INT)

		# baselineNode.SetAndObserveImageData(VTK_baseline)
		# followupNode.SetAndObserveImageData(VTK_followup)
		# # baselineNode.Modified()
		# # followupNode.GetImageData().Modified()

		# baselineArray = slicer.util.array(baselineLabel)
		# print baselineArray[100,190,:]

