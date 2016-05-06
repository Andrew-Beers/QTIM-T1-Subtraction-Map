from __main__ import qt, ctk, slicer

from BeersSingleStep import *
from Helper import *

class VolumeSelectStep( BeersSingleStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '1. Volume Selection' )
    self.setDescription( 'Select the pre- and post-contrast volumes to calculate the subtraction map.' )

    self.__parent = super( VolumeSelectStep, self )

  def createUserInterface( self ):
    '''
    '''
    self.__layout = self.__parent.createUserInterface()
   
    baselineScanLabel = qt.QLabel( 'Baseline scan:' )
    self.__baselineVolumeSelector = slicer.qMRMLNodeComboBox()
    self.__baselineVolumeSelector.toolTip = "Choose the pre-contrast scan"
    self.__baselineVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.__baselineVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.__baselineVolumeSelector.addEnabled = 0

    followupScanLabel = qt.QLabel( 'Followup scan:' )
    self.__followupVolumeSelector = slicer.qMRMLNodeComboBox()
    self.__followupVolumeSelector.toolTip = "Choose the post-contrast scan"
    self.__followupVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.__followupVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.__followupVolumeSelector.addEnabled = 0

    loadDataButton = qt.QPushButton('Load test data')
    self.__layout.addRow(loadDataButton)
    loadDataButton.connect('clicked()', self.loadData)

    self.__layout.addRow( baselineScanLabel, self.__baselineVolumeSelector )
    self.__layout.addRow( followupScanLabel, self.__followupVolumeSelector )

    self.updateWidgetFromParameters(self.parameterNode())

    qt.QTimer.singleShot(0, self.killButton)

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='Page2')
    if len(bl):
      bl[0].hide()

  def loadData(self):
    vl = slicer.modules.volumes.logic()
    vol1 = vl.AddArchetypeVolume('http://www.slicer.org/slicerWiki/images/5/59/RegLib_C01_1.nrrd', 'Meningioma1', 0)
    vol2 = vl.AddArchetypeVolume('http://www.slicer.org/slicerWiki/images/e/e3/RegLib_C01_2.nrrd', 'Meningioma2', 0)
    if vol1 != None and vol2 != None:
      self.__baselineVolumeSelector.setCurrentNode(vol1)
      self.__followupVolumeSelector.setCurrentNode(vol1)
      Helper.SetBgFgVolumes(vol1.GetID(), vol2.GetID())
    else:
      print 'LoadData Failed'


  def validate( self, desiredBranchId ):
    '''
    '''
    # self.__parent.validationSucceeded(desiredBranchId)
    self.__parent.validate( desiredBranchId )

    # check here that the selectors are not empty
    baseline = self.__baselineVolumeSelector.currentNode()
    followup = self.__followupVolumeSelector.currentNode()

    if baseline != None and followup != None:
      baselineID = baseline.GetID()
      followupID = followup.GetID()
      if baselineID != '' and followupID != '' and baselineID != followupID:
    
        pNode = self.parameterNode()
        pNode.SetParameter('baselineVolumeID', baselineID)
        pNode.SetParameter('followupVolumeID', followupID)

        self.__parent.validationSucceeded(desiredBranchId)
      else:
        self.__parent.validationFailed(desiredBranchId, 'Error','Please select distinctive baseline and followup volumes!')
    else:
      self.__parent.validationFailed(desiredBranchId, 'Error','Please select both baseline and followup volumes!')

  def onEntry(self, comingFrom, transitionType):

    super(VolumeSelectStep, self).onEntry(comingFrom, transitionType)
    self.updateWidgetFromParameters(self.parameterNode())
    pNode = self.parameterNode()
    pNode.SetParameter('currentStep', self.stepid)

    qt.QTimer.singleShot(0, self.killButton)

  def onExit(self, goingTo, transitionType):   
    # extra error checking, in case the user manages to click ReportROI button
    super(BeersSingleStep, self).onExit(goingTo, transitionType) 

  def updateWidgetFromParameters(self, parameterNode):
    baselineVolumeID = parameterNode.GetParameter('baselineVolumeID')
    followupVolumeID = parameterNode.GetParameter('followupVolumeID')
    if baselineVolumeID != None:
      self.__baselineVolumeSelector.setCurrentNode(Helper.getNodeByID(baselineVolumeID))
    if followupVolumeID != None:
      self.__followupVolumeSelector.setCurrentNode(Helper.getNodeByID(followupVolumeID))
