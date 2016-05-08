""" This is Step 2. The user has the option to register their pre- and post-contrast images.
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

""" RegistrationStep inherits from BeersSingleStep, with itself inherits
	from a ctk workflow class. 
"""

class RegistrationStep( BeersSingleStep ) :
	
	def __init__( self, stepid ):

		""" This method creates a drop-down menu that includes the whole step.
		The description also acts as a tooltip for the button. There may be 
		some way to override this. The initialize method is presumably inherited
		from ctk.
		"""

		self.initialize( stepid )
		self.setName( '2. Registration' )
		self.setDescription( """Please select your preferred method of registration. If you have already registered your images, or no registration is required, check the option "No Registration." Be aware that many other modules in Slicer have more complex and/or customizable registration methods, should the methods in this step prove insufficient.
			""")

		self.__parent = super( RegistrationStep, self )

		self.__status = "Uncalled"
	
	def createUserInterface( self ):
		
		""" This method uses qt to create a user interface of radio buttons to select
		a registration method. Note that BSpline registration is so slow and memory-consuming
		as to at one point break Slicer. There is an option to run it with limited memory,
		but this may take prohibitively long.
		"""

		self.__layout = self.__parent.createUserInterface()

		RegistrationGroupBox = qt.QGroupBox()
		RegistrationGroupBox.setTitle('Registration Method')
		self.__layout.addRow(RegistrationGroupBox)

		RegistrationGroupBoxLayout = qt.QFormLayout(RegistrationGroupBox)

		# self.RegistrationRadio = qt.QFrame()
		# self.RegistrationRadio.setLayout(qt.QVBoxLayout())
		# self.__layout.addWidget(self.RegistrationRadio)

		self.radio1 = qt.QRadioButton("No Registration")
		self.radio1.toolTip = "Performs no registration."
		RegistrationGroupBoxLayout.addRow(self.radio1)
		self.radio1.setChecked(True)

		self.radio2 = qt.QRadioButton("Rigid Registration (Fastest)")
		self.radio2.toolTip = """Computes a rigid registration on the pre-contrast image with respect to the post-contrast image. This is likely to be the fastest registration method"""
		RegistrationGroupBoxLayout.addRow(self.radio2)

		self.radio3 = qt.QRadioButton("Affine Registration")
		self.radio3.toolTip = "Computes a rigid and affine registration on the pre-contrast image with respect to the post-contrast image."
		RegistrationGroupBoxLayout.addRow(self.radio3)
		
		self.radio4 = qt.QRadioButton("BSpline Registration (Slowest)")
		self.radio4.toolTip = """Computes a BSpline Registration on the pre-contrast image with respect to the post-contrast image. This method is slowest and may be necessary for only severly distorted images."""
		RegistrationGroupBoxLayout.addRow(self.radio4)

		self.__registrationButton = qt.QPushButton('Run registration')
		self.__registrationStatus = qt.QLabel('Register scans')
		self.__layout.addRow(self.__registrationStatus, self.__registrationButton)
		self.__registrationButton.connect('clicked()', self.onRegistrationRequest)

	def killButton(self):

		# ctk creates a useless final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='NormalizationStep')
		if len(bl):
			bl[0].hide()


	def validate(self, desiredBranchId):

		""" This checks to make sure you are not currently registering an image, and
	  		throws an exception if so.
		"""

		self.__parent.validate( desiredBranchId )

		if self.__status == 'Uncalled' or self.__status == 'Completed':
			self.__parent.validationSucceeded(desiredBranchId)
		else:
			self.__parent.validationFailed(desiredBranchId, 'Error','Please wait until registration is completed')

	def onEntry(self, comingFrom, transitionType):
		super(RegistrationStep, self).onEntry(comingFrom, transitionType)
		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)
		
		# A different attempt to get rid of the extra workflow button.
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	def onRegistrationRequest(self):

		""" This method makes a call to a differen Slicer module, Expert Automated
			Registration. It is a command line interface (CLI) module that comes 
			pre-packaged with Slicer. It may be useful to develop a check, in case
			someone is using a version of slicer without this module. Other modules
			are avaliable too, such as BRAINSfit. Note that this registration method
			computes a transform, which is then applied to the followup volume in
			processRegistrationCompletion.
		"""

		pNode = self.parameterNode()
		baselineVolumeID = pNode.GetParameter('baselineVolumeID')
		followupVolumeID = pNode.GetParameter('followupVolumeID')

		self.__followupTransform = slicer.vtkMRMLBSplineTransformNode()
		slicer.mrmlScene.AddNode(self.__followupTransform)

		parameters = {}
		parameters["fixedImage"] = baselineVolumeID
		parameters["movingImage"] = followupVolumeID
		parameters['saveTransform'] = self.__followupTransform.GetID()
		parameters['registration'] = 'Rigid'

		self.__cliNode = None
		self.__cliNode = slicer.cli.run(slicer.modules.expertautomatedregistration, self.__cliNode, parameters)

		# An event listener for the CLI. To-Do: Add a progress bar.
		self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
		self.__registrationStatus.setText('Wait ...')
		self.__registrationButton.setEnabled(0)


	def processRegistrationCompletion(self, node, event):

		""" This updates the registration button with the CLI module's convenient status
			indicator. Upon completion, it applies the transform to the followup node.
			Furthermore, it sets the followup node to be the baseline node in the viewer.
			It also saves the transform for later in the parameter node.
		"""

		self.__status = node.GetStatusString()
		self.__registrationStatus.setText('Registration ' + self.__status)

		if self.__status == 'Completed':
			self.__registrationButton.setEnabled(1)

			pNode = self.parameterNode()
			followupNode = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
			followupNode.SetAndObserveTransformNodeID(self.__followupTransform.GetID())
		
			Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

			pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())

