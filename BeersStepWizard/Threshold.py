""" This is Step 5. The user has the option to normalize intensity values
	across pre- and post-contrast images.
"""

from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

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
		self.setDescription( 'If so desired, normalize your images by dividing them by their standard deviations.' )

		self.__parent = super( ThresholdStep, self )

	def createUserInterface( self ):

		""" As of now, this step's UI is fairly simple. If there are other methods of
			normalization, they could be added here.
		"""

		self.__layout = self.__parent.createUserInterface()

		self.__normalizationButton = qt.QPushButton('Run Gaussian Normalization')

		self.__layout.addRow(self.__normalizationButton)


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
		pNode.SetParameter('currentStep', self.stepid)
		
		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   
		# extra error checking, in case the user manages to click ReportROI button
		super(BeersSingleStep, self).onExit(goingTo, transitionType) 

	