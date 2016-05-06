from __main__ import vtk, qt, ctk, slicer

import BeersStepWizard

class BeersStep:

	#Example Extension Definitions

	def __init__( self, parent ):
		parent.title = """BeersStepTaker"""
		parent.categories = ["""Examples"""]
		parent.contributors = ["""Andrew Beers"""]
		parent.helpText = """
		A step by step template derived from ChangeTracker
		""";
		parent.acknowledgementText = """Hopefully, this work leads to a job at the QTIM
		"""
		self.parent = parent
		self.collapsed = False

class BeersStepWidget():

	#Don't yet know what this does

	def __init__( self, parent=None ):
		if not parent:
				self.parent = slicer.qMRMLWidget()
				self.parent.setLayout( qt.QVBoxLayout() )
				self.parent.setMRMLScene( slicer.mrmlScene )
		else:
			self.parent = parent
			self.layout = self.parent.layout()

	def setup( self ):

		#This starts our workflow.

		self.workflow = ctk.ctkWorkflow()

		workflowWidget = ctk.ctkWorkflowStackedWidget()
		workflowWidget.setWorkflow( self.workflow )

		# create all wizard steps
		self.Step1 = BeersStepWizard.VolumeSelectStep( 'VolumeSelectStep'  )
		self.Step2 = BeersStepWizard.RegistrationStep( 'RegistrationStep'  )
		self.Step3 = BeersStepWizard.NormalizationStep( 'NormalizationStep'  )

		# add the wizard steps to an array for convenience
		allSteps = []

		allSteps.append( self.Step1 )
		allSteps.append( self.Step2 )
		allSteps.append( self.Step3 )

		# Add transition for the first step which let's the user choose between simple and advanced mode
		self.workflow.addTransition( self.Step1, self.Step2 )
		self.workflow.addTransition( self.Step2, self.Step3 )

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

		for s in allSteps:
				s.setParameterNode (self.parameterNode)

		# restore workflow step
		currentStep = self.parameterNode.GetParameter('currentStep')
		if currentStep != '':
			print 'Restoring workflow step to ', currentStep
			if currentStep == 'Page1':
				self.workflow.setInitialStep(self.Step1)
			if currentStep == 'Page2':
				self.workflow.setInitialStep(self.Step2)
			if currentStep == 'Page3':
				self.workflow.setInitialStep(self.Step3)
		else:
			print 'currentStep in parameter node is empty!'

		# start the workflow and show the widget
		self.workflow.start()
		workflowWidget.visible = True
		self.layout.addWidget( workflowWidget )

		# enable global access to the dynamicFrames on step 2 and step 6
		#slicer.modules.emsegmentSimpleDynamicFrame = defineInputChannelsSimpleStep.dynamicFrame()
		#slicer.modules.emsegmentAdvancedDynamicFrame = definePreprocessingStep.dynamicFrame()

		# compress the layout
			#self.layout.addStretch(1)


	def enter(self):
		print "BeersStep Template Called"