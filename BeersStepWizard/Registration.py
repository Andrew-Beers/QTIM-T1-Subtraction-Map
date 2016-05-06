from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

class RegistrationStep( BeersSingleStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '2. Registration' )
    self.setDescription( 'Please select your preferred method of registration. If you have already registered your images, or no registration is required, check the option "No Registration." Be aware that many other modules in Slicer have more complex and/or customizable registration methods, should the methods in this step prove insufficient.' )

    self.__parent = super( RegistrationStep, self )

  def createUserInterface( self ):
    '''
    '''
    self.__layout = self.__parent.createUserInterface()

    # self.chartOptions = ("Count", "Volume mm^3", "Volume cc", "Min", "Max", "Mean", "StdDev")

    self.RegistrationRadio = qt.QFrame()
    self.RegistrationRadio.setLayout(qt.QVBoxLayout())
    self.__layout.addWidget(self.RegistrationRadio)
    self.radio1 = qt.QRadioButton("BSpline Registration")
    self.radio1.toolTip = "Computes a BSpline Registration on the pre-contrast image with respect to the post-contrast image."
    self.RegistrationRadio.layout().addWidget(self.radio1)
    self.radio1.setChecked(True)
    # self.radio2 = qt.QRadioButton("No Registration")
    # self.radio2.toolTip = "Continue with images as-is."
    # self.RegistrationRadio.layout().addWidget(self.radio2)
    self.RegistrationRadio.enabled = True

    self.__registrationButton = qt.QPushButton('Run registration')
    self.__registrationStatus = qt.QLabel('Register scans')

    self.__layout.addRow(self.__registrationStatus, self.__registrationButton)

    self.__registrationButton.connect('clicked()', self.onRegistrationRequest)

    # self.chartFrame = qt.QFrame()
    # self.chartFrame.setLayout(qt.QHBoxLayout())
    # self.__layout.addWidget(self.chartFrame)
    # self.chartButton = qt.QPushButton("Chart")
    # self.chartButton.toolTip = "Make a chart from the current statistics."
    # self.chartFrame.layout().addWidget(self.chartButton)
    # self.chartOption = qt.QComboBox()
    # self.chartOption.addItems(self.chartOptions)
    # self.chartFrame.layout().addWidget(self.chartOption)
    # self.chartIgnoreZero = qt.QCheckBox()
    # self.chartIgnoreZero.setText('Ignore Zero')
    # self.chartIgnoreZero.checked = False
    # self.chartIgnoreZero.setToolTip('Do not include the zero index in the chart to avoid dwarfing other bars')
    # self.chartFrame.layout().addWidget(self.chartIgnoreZero)
    # self.chartFrame.enabled = False

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='NormalizationStep')
    if len(bl):
      bl[0].hide()

  def validate(self, desiredBranchId):
    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self, comingFrom, transitionType):
    super(RegistrationStep, self).onEntry(comingFrom, transitionType)
    pNode = self.parameterNode()
    pNode.SetParameter('currentStep', self.stepid)
    
    qt.QTimer.singleShot(0, self.killButton)

  def onExit(self, goingTo, transitionType):   
    # extra error checking, in case the user manages to click ReportROI button

    super(BeersSingleStep, self).onExit(goingTo, transitionType) 

  def onRegistrationRequest(self):

    # rigidly register followup to baseline
    # TODO: do this in a separate step and allow manual adjustment?
    # TODO: add progress reporting (BRAINSfit does not report progress though)
    pNode = self.parameterNode()
    baselineVolumeID = pNode.GetParameter('baselineVolumeID')
    print baselineVolumeID
    a = slicer.util.array(baselineVolumeID)
    print a[100,100,:]
    print Helper.getNodeByID(baselineVolumeID)
    followupVolumeID = pNode.GetParameter('followupVolumeID')
    self.__followupTransform = slicer.vtkMRMLBSplineTransformNode()
    slicer.mrmlScene.AddNode(self.__followupTransform)

    # parameters = {}
    # parameters["fixedVolume"] = baselineVolumeID
    # parameters["movingVolume"] = followupVolumeID
    # parameters["initializeTransformMode"] = "useMomentsAlign"
    # parameters["useRigid"] = True
    # parameters["useScaleVersor3D"] = True
    # parameters["useScaleSkewVersor3D"] = True
    # parameters["useAffine"] = True
    # parameters["linearTransform"] = self.__followupTransform.GetID()

    parameters = {}
    parameters["fixedImage"] = baselineVolumeID
    parameters["movingImage"] = followupVolumeID
    parameters['saveTransform'] = self.__followupTransform.GetID()
    parameters['registration'] = 'Rigid'

    self.__cliNode = None
    self.__cliNode = slicer.cli.run(slicer.modules.expertautomatedregistration, self.__cliNode, parameters)

    self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
    self.__registrationStatus.setText('Wait ...')
    self.__registrationButton.setEnabled(0)


  def processRegistrationCompletion(self, node, event):
    status = node.GetStatusString()
    self.__registrationStatus.setText('Registration '+status)
    if status == 'Completed':
      self.__registrationButton.setEnabled(1)
  
      pNode = self.parameterNode()
      followupNode = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
      followupNode.SetAndObserveTransformNodeID(self.__followupTransform.GetID())
      
      Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

      pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())
      # print pNode.GetParameter('baselineVolumeID').GetImageData()

