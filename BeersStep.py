""" This file is picked up by 3D Slicer and used to create a widget. BeersStep
	(the class) specifies the Help and Acknowledgements qt box seen in Slicer.
	BeersStepWidget start the main action of the module, creating a workflow
	from ctk and creating initial links to Slicer's MRML data. Most of this
	module is modeled after ChangeTracker by Fedorov, which can be found in
	the following GitHub repository: https://github.com/fedorov/ChangeTrackerPy


	vtk is a libary associated with image processing, ctk a refined version of
	vtk meant specifically for medical imaging and used to here to create a
	step-by-step workflow, qt a popular user interface library, and slicer.
	The program 3D Slicer has access to these libraries (and more), and is
	referenced here as __main__. BeersStepWizard is a folder that contains
	the individual steps of the workflow and does most of the computational
	work. 


	 All the best, Andrew Beers
"""

from __main__ import vtk, qt, ctk, slicer

import BeersStepWizard

class BeersStep:

	def __init__( self, parent ):

		""" This class specifies the Help + Acknowledgements section. One assumes
			that Slicer looks for a class with the same name as the file name. 
			Modifications to the parent result in modifications to the qt box that 
			contains the relevant information.
		"""

		parent.title = """BeersStepTaker"""
		parent.categories = ["""Examples"""]
		parent.contributors = ["""Andrew Beers"""]
		parent.helpText = """
		A step by step template derived from ChangeTracker
		""";
		parent.acknowledgementText = """Andrew Beers, Brown University
		"""
		self.parent = parent
		self.collapsed = False

class BeersStepWidget:

	def __init__( self, parent=None ):

		""" It seems to be that Slicer creates an instance of this class with a
			qMRMLWidget parent. If for some reason it doesn't, this __init__ will.
		"""

		if not parent:
				self.parent = slicer.qMRMLWidget()
				self.parent.setLayout( qt.QVBoxLayout() )
				self.parent.setMRMLScene( slicer.mrmlScene )
		else:
			self.parent = parent
			self.layout = self.parent.layout()

	def setup( self ):

		""" Slicer seems to call all methods of these classes upon entry. setup creates
			a workflow from ctk, which simply means that it creates a certies of UI
			steps one can traverse with "next" / "previous" buttons. The steps themselves
			are contained within BeersStepWizard.
		"""

		# Currently unclear on the difference between ctkWorkflow and
		# ctkWorkflowStackedWidget, but presumably the latter creates a UI
		# for the former
		self.workflow = ctk.ctkWorkflow()
		workflowWidget = ctk.ctkWorkflowStackedWidget()
		workflowWidget.setWorkflow( self.workflow )

		# Create workflow steps.
		self.Step1 = BeersStepWizard.VolumeSelectStep('VolumeSelectStep')
		self.Step2 = BeersStepWizard.RegistrationStep('RegistrationStep')
		self.Step3 = BeersStepWizard.NormalizeSubtractStep('NormalizeSubtractStep')
		self.Step4 = BeersStepWizard.ROIStep('ROIStep')
		self.Step5 = BeersStepWizard.ThresholdStep('ThresholdStep')

		# Add the wizard steps to an array for convenience. Much of the following code
		# is copied wholesale from ChangeTracker.
		allSteps = []
		allSteps.append( self.Step1 )
		allSteps.append( self.Step2 )
		allSteps.append( self.Step3 )
		allSteps.append( self.Step4 )
		allSteps.append( self.Step5 )

		# Adds transition functionality between steps.
		self.workflow.addTransition(self.Step1, self.Step2)
		self.workflow.addTransition(self.Step2, self.Step3)
		self.workflow.addTransition(self.Step3, self.Step4)
		self.workflow.addTransition(self.Step4, self.Step5)

		# The following code creates a so-called parameter node referencing the
		# vtkMRMLScriptedModuleNode class, while checking to make sure one doesn't
		# already exist for some reason. This node keeps track of changse to MRML scene.
		nNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScriptedModuleNode')
		self.parameterNode = None
		for n in xrange(nNodes):
			compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLScriptedModuleNode')
			nodeid = None
			if compNode.GetModuleName() == 'BeersStepTaker':
				self.parameterNode = compNode
				print 'Found existing BeersStepTaker parameter node'
				break
		if self.parameterNode == None:
			self.parameterNode = slicer.vtkMRMLScriptedModuleNode()
			self.parameterNode.SetModuleName('BeersStepTaker')
			slicer.mrmlScene.AddNode(self.parameterNode)

		# Individual steps get access to the parameter node too!
		for s in allSteps:
				s.setParameterNode (self.parameterNode)

		# Restores workflow step in case something goes wrong.
		currentStep = self.parameterNode.GetParameter('currentStep')
		if currentStep != '':
			print 'Restoring workflow step to ', currentStep
			if currentStep == 'Page1':
				self.workflow.setInitialStep(self.Step1)
			if currentStep == 'Page2':
				self.workflow.setInitialStep(self.Step2)
			if currentStep == 'Page3':
				self.workflow.setInitialStep(self.Step3)
			if currentStep == 'Page4':
				self.workflow.setInitialStep(self.Step4)
			if currentStep == 'Page5':
				self.workflow.setInitialStep(self.Step4)
		else:
			print 'currentStep in parameter node is empty!'

		# Starts and show the workflow.
		self.workflow.start()
		workflowWidget.visible = True
		self.layout.addWidget( workflowWidget )

	def enter(self):
		""" A quick check to see if the file was loaded. Can be seen in the Python Interactor.
		"""

		print "BeersStep Template Called"