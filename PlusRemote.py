from __main__ import vtk, qt, ctk, slicer
import datetime
#
# PlusRemote
#

class PlusRemote:
  def __init__(self, parent):
    parent.title = "Plus Remote"
    parent.categories = ["IGT"]
    parent.contributors = ["Franklin King (Queen's University), Tamas Ungi (Queen's University)"]
    parent.helpText = """
    This is a convenience module for sending commands through OpenIGTLink Remote to PLUS. See <a>https://www.assembla.com/spaces/plus/wiki/PlusServer_commands</a> for more information about Plus Server commands.
    """
    parent.acknowledgementText = """
    This work was funded by Cancer Care Ontario and the Ontario Consortium for Adaptive Interventions in Radiation Oncology (OCAIRO)
"""
    #parent.icon = qt.QIcon(":Icons/PlusRemote.png")
    self.parent = parent

    
#
# qPlusRemoteWidget
#
class PlusRemoteWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    self.lastCommandId = 0
    self.timeoutCounter = 0
    if not parent:
      self.setup()
      self.parent.show()

    self.currentDirectory = '.'
    self.plusRemoteModuleDirectoryPath = slicer.modules.plusremote.path.replace("PlusRemote.py","")

      
  def setup(self):
    # Instantiate and connect widgets
    
    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)    
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "PlusRemote Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    #reloadFormLayout.addWidget(self.reloadAndTestButton)
    #self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

   
    # Module requires openigtlinkremote
    try:
      slicer.modules.openigtlinkremote
    except:
      self.errorLabel = qt.QLabel("Could not find OpenIGTLink Remote module")
      self.layout.addWidget(self.errorLabel)
      return      
   
    # IGTLink Connector
    connectorCollapsibleButton = ctk.ctkCollapsibleButton()
    connectorCollapsibleButton.text = "OpenIGTLink Connector"
    self.layout.addWidget(connectorCollapsibleButton)    
    connectorLayout = qt.QFormLayout(connectorCollapsibleButton)    
    
    self.linkInputSelector = slicer.qMRMLNodeComboBox()
    self.linkInputSelector.nodeTypes = ( ("vtkMRMLIGTLConnectorNode"), "" )
    self.linkInputSelector.selectNodeUponCreation = True
    self.linkInputSelector.addEnabled = False
    self.linkInputSelector.removeEnabled = True
    self.linkInputSelector.noneEnabled = False
    self.linkInputSelector.showHidden = False
    self.linkInputSelector.showChildNodeTypes = False
    self.linkInputSelector.setMRMLScene( slicer.mrmlScene )
    self.linkInputSelector.setToolTip( "Pick connector node" )
    connectorLayout.addRow("OpenIGTLinkConnector: ", self.linkInputSelector)    
    
    # Recording
    
    self.recordingCollapsibleButton = ctk.ctkCollapsibleButton()
    self.recordingCollapsibleButton.text = "Recording"
    self.recordingCollapsibleButton.enabled = False
    self.layout.addWidget(self.recordingCollapsibleButton)    
    recordingLayout = qt.QFormLayout(self.recordingCollapsibleButton)

    self.captureIDBox = qt.QLineEdit()
    # recordingLayout.addRow("Capture Device ID: ", self.captureIDBox)    
        
    self.directoryButton = ctk.ctkDirectoryButton()
    recordingLayout.addRow("Output Directory: ", self.directoryButton)

    # Move to the same row, use grid layout
    self.recordIcon = qt.QIcon(self.plusRemoteModuleDirectoryPath+'/Resources/Icons/icon_Record.png')
    self.stopIcon = qt.QIcon(self.plusRemoteModuleDirectoryPath+'/Resources/Icons/icon_Stop.png')
    self.recordingButton = qt.QPushButton('Start Recording')
    self.recordingButton.checkable = True
    self.recordingButton.setIcon(self.recordIcon)
    recordingLayout.addRow(self.recordingButton)
    
    # self.stopRecordingButton = qt.QPushButton("Stop Recording")
    # recordingLayout.addRow(self.stopRecordingButton)
     
    # Reconstruction
    self.reconstructionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.reconstructionCollapsibleButton.text = "Reconstruction"
    self.reconstructionCollapsibleButton.enabled = False
    self.layout.addWidget(self.reconstructionCollapsibleButton)    
    reconstructionLayout = qt.QFormLayout(self.reconstructionCollapsibleButton)

    # Move to the same row, use grid layout
    self.startReconstuctionButton = qt.QPushButton("Start Reconstruction")
    # reconstructionLayout.addRow(self.startReconstuctionButton)
    
    self.stopReconstructionButton = qt.QPushButton("Stop Reconstruction")
    # reconstructionLayout.addRow(self.stopReconstructionButton)
    
    self.fileNameBox = qt.QLineEdit()
    reconstructionLayout.addRow("Tracked Image Sequence Filename: ", self.fileNameBox)
  
    self.reconstructVolumeButton = qt.QPushButton("Reconstruct Recorded Volume")
    reconstructionLayout.addRow(self.reconstructVolumeButton)
    
    # Transform Update
    self.transformUpdateCollapsibleButton = ctk.ctkCollapsibleButton()
    self.transformUpdateCollapsibleButton.text = "Transform Update"
    self.transformUpdateCollapsibleButton.enabled = False
    self.layout.addWidget(self.transformUpdateCollapsibleButton)    
    transformUpdateLayout = qt.QFormLayout(self.transformUpdateCollapsibleButton)
    
    self.transformUpdateInputSelector = slicer.qMRMLNodeComboBox()
    self.transformUpdateInputSelector.nodeTypes = ( ("vtkMRMLLinearTransformNode"), "" )
    self.transformUpdateInputSelector.selectNodeUponCreation = True
    self.transformUpdateInputSelector.addEnabled = False
    self.transformUpdateInputSelector.removeEnabled = True
    self.transformUpdateInputSelector.renameEnabled = True
    self.transformUpdateInputSelector.noneEnabled = False
    self.transformUpdateInputSelector.showHidden = False
    self.transformUpdateInputSelector.showChildNodeTypes = False
    self.transformUpdateInputSelector.setMRMLScene( slicer.mrmlScene )
    self.transformUpdateInputSelector.setToolTip( "Pick transform node" )
    transformUpdateLayout.addRow("Transform node: ", self.transformUpdateInputSelector)
    
    self.updateTransformButton = qt.QPushButton("Update")
    transformUpdateLayout.addRow(self.updateTransformButton)

    self.configFileNameBox = qt.QLineEdit()
    transformUpdateLayout.addRow("Filename: ", self.configFileNameBox)
    
    self.saveTransformButton = qt.QPushButton("Save Config")
    transformUpdateLayout.addRow(self.saveTransformButton)
    
    self.replyUpdateCollapsibleButton = ctk.ctkCollapsibleButton()
    self.replyUpdateCollapsibleButton.text = "Reply"
    self.replyUpdateCollapsibleButton.enabled = False
    self.layout.addWidget(self.replyUpdateCollapsibleButton)    
    replyLayout = qt.QFormLayout(self.replyUpdateCollapsibleButton)
    
    self.replyBox = qt.QPlainTextEdit()
    self.replyBox.setReadOnly(True)
    replyLayout.addRow(self.replyBox)
    
    # connections
    self.linkInputSelector.connect('currentNodeChanged(bool)', self.enableOrDisableCollapsibleButtons)
    self.recordingButton.connect('toggled(bool)', self.onRecording)
    
    self.startReconstuctionButton.connect('clicked(bool)', self.onStartReconstruction)
    self.stopReconstructionButton.connect('clicked(bool)', self.onStopReconstruction)
    self.reconstructVolumeButton.connect('clicked(bool)', self.onReconstVolume)
    self.directoryButton.connect('directoryChanged(const QString &)',self.onDirectoryButton)

    self.updateTransformButton.connect('clicked(bool)', self.onUpdateTransform)
    self.saveTransformButton.connect('clicked(bool)', self.onSaveTransform)

    self.layout.addStretch(1)
      
  
  def cleanup(self):
    pass

  def enableOrDisableCollapsibleButtons(self):
    self.recordingCollapsibleButton.enabled = self.linkInputSelector.currentNode() != None
    self.reconstructionCollapsibleButton.enabled = self.linkInputSelector.currentNode() != None
    self.transformUpdateCollapsibleButton.enabled = self.linkInputSelector.currentNode() != None
    self.replyUpdateCollapsibleButton.enabled = self.linkInputSelector.currentNode() != None

  def onRecording(self,status):
    print status
    if status == True:
      self.outputFileName = "TrackedImageSequence_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".mha"
      self.fileNameBox.text = self.outputFileName
      self.recordingButton.setText('Stop Recording')
      self.recordingButton.setIcon(self.stopIcon)
      logic = PlusRemoteLogic()
      self.lastCommandId = logic.startRecording(self.linkInputSelector.currentNode().GetID(),
      self.captureIDBox.text, self.currentDirectory, self.outputFileName)
      self.setTimer()
    else:
      self.recordingButton.setText('Start Recording')
      self.recordingButton.setIcon(self.recordIcon)
      logic = PlusRemoteLogic()
      self.lastCommandId = logic.stopRecording(self.linkInputSelector.currentNode().GetID(), self.captureIDBox.text)
      self.setTimer()
      
  def onStartReconstruction(self):
    logic = PlusRemoteLogic()
    self.lastCommandId = logic.startVolumeReconstuction( self.linkInputSelector.currentNode().GetID())
    self.setTimer()
  
  def onStopReconstruction(self):
    logic = PlusRemoteLogic()
    self.lastCommandId = logic.stopVolumeReconstruction(self.linkInputSelector.currentNode().GetID())
    self.setTimer()

  def onReconstVolume(self):
    reconstructionOutputFileName = "Recon_" +self.fileNameBox.text[21:] +"_"+ datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".mha" 
    logic = PlusRemoteLogic()
    self.lastCommandId = logic.reconstructRecorded(self.linkInputSelector.currentNode().GetID(),
        self.currentDirectory, self.fileNameBox.text, reconstructionOutputFileName)
    self.setTimer()

  def onDirectoryButton(self):
    self.currentDirectory = self.directoryButton.directory
    print self.currentDirectory

  def onUpdateTransform(self):
    logic = PlusRemoteLogic()
    self.lastCommandId = logic.updateTransform(self.linkInputSelector.currentNode().GetID(), self.transformUpdateInputSelector.currentNode())
    self.setTimer()
    
  def onSaveTransform(self):
    logic = PlusRemoteLogic()
    self.lastCommandId = logic.saveTransform(self.linkInputSelector.currentNode().GetID(), self.configFileNameBox.text)
    self.setTimer()
  
  def setTimer(self):
    self.replyBox.setPlainText("Waiting for reply...")
    self.timeoutCounter = 0
    self.timer = qt.QTimer()
    self.timer.timeout.connect(self.getCommandReply)
    self.timer.start(100)
  
  def getCommandReply(self):
    logic = PlusRemoteLogic()
    replyNodes = slicer.mrmlScene.GetNodesByName( "ACK_" + str(self.lastCommandId) )
    textNode = slicer.vtkMRMLAnnotationTextNode.SafeDownCast( replyNodes.GetItemAsObject(0) )
    if textNode:
      self.replyBox.setPlainText(textNode.GetText(0))
      logic.discardCommand(self.lastCommandId, self.linkInputSelector.currentNode().GetID())
      self.timer.stop()
    elif self.timeoutCounter >= 500:
      self.replyBox.setPlainText("No reply: Timeout")
      logic.discardCommand(self.lastCommandId, self.linkInputSelector.currentNode().GetID())
      self.timer.stop()
    else:
      self.timeoutCounter += 1

  def onReload(self,moduleName="PlusRemote"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer
    import vtk, qt, ctk
    import datetime
    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

#
# PlusRemoteLogic
#
class PlusRemoteLogic:
  def __init__(self):
    pass
  
  def startVolumeReconstuction(self, connectorNodeId):
    #parameters = "VolumeReconstructorDeviceId=" + "\"" 
    parameters = ""
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "StartVolumeReconstruction", parameters)
    return commandCounter
  
  #def stopVolumeReconstruction(self, volumeReconstructorDeviceId, ouputVolDeviceName, ouputVolFileName): 
  def stopVolumeReconstruction(self, connectorNodeId):
    #parameters = "VolumeReconstructorDeviceID=" + "\"" + volumeReconstructorDeviceId + "OutputVolumeDeviceName" + "\"" + "OutputVolFileName" + "\"" + outputVolFileName
    parameters = ""
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "StopVolumeReconstruction", parameters)
    return commandCounter
  
  def reconstructRecorded(self, connectorNodeId, directory, fileName, reconstructionOutputFileName):
    parameters = "InputSeqFilename=" + "\"" + directory + "/" + fileName + "\""+ " OutputVolFilename=" + "\"" + directory + "/"+ reconstructionOutputFileName+"\""
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "ReconstructVolume", parameters)
    print parameters
    return commandCounter
  
  def startRecording(self, connectorNodeId, captureName, directory, outputFileName):
    parameters = "CaptureDeviceID=" + "\"" + captureName + "\"" + " OutputFilename=" + "\""  + directory + "/"+ outputFileName + "\""
    print 'recording parameters', parameters
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "StartRecording", parameters)
    return commandCounter
  
  def stopRecording(self, connectorNodeId, captureName):
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "StopRecording", "CaptureDeviceID=" + "\"" + captureName + "\"")
    return commandCounter
  
  def updateTransform(self, connectorNodeId, transformNode):
    transformMatrix = transformNode.GetMatrixTransformToParent()
    transformValue = ""
    for i in range(0,4):
      for j in range(0,4):
        transformValue = transformValue + str(transformMatrix.GetElement(i,j)) + " "
    
    transformDate = str(datetime.datetime.now())
    
    parameters = "TransformName=" + "\"" + transformNode.GetName() + "\"" + " TransformValue=" + "\"" + transformValue + "\" " + "TransformDate=" + "\"" + transformDate + "\""
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "UpdateTransform", parameters)
    return commandCounter
    
  def saveTransform(self, connectorNodeId, filename):
    parameters = "Filename=" + "\"" + filename + "\""
    commandCounter = slicer.modules.openigtlinkremote.logic().ExecuteCommand(connectorNodeId, "SaveConfig", parameters)
    return commandCounter
    
  def discardCommand(self, commandId, connectorNodeId):
    slicer.modules.openigtlinkremote.logic().DiscardCommand(commandId, connectorNodeId)

