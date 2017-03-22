import slicer
import os
import ctk
import vtk
import qt
import logging
from ...constants import SliceTrackerConstants as constants
from ...helpers import NewCaseSelectionNameWidget
from SlicerProstateUtils.decorators import logmethod
from SlicerProstateUtils.helpers import WatchBoxAttribute, BasicInformationWatchBox

from ..base import SliceTrackerPlugin, SliceTrackerLogicBase


class SliceTrackerCaseManagerLogic(SliceTrackerLogicBase):

  def __init__(self):
    super(SliceTrackerCaseManagerLogic, self).__init__()

  def cleanup(self):
    pass


class SliceTrackerCaseManagerPlugin(SliceTrackerPlugin):

  LogicClass = SliceTrackerCaseManagerLogic
  NAME = "CaseManager"

  @property
  def caseRootDir(self):
    return self.casesRootDirectoryButton.directory

  @caseRootDir.setter
  def caseRootDir(self, path):
    try:
      exists = os.path.exists(path)
    except TypeError:
      exists = False
    self.setSetting('CasesRootLocation', path if exists else None)
    self.casesRootDirectoryButton.text = self.truncatePath(path) if exists else "Choose output directory"
    self.casesRootDirectoryButton.toolTip = path
    self.openCaseButton.enabled = exists
    self.createNewCaseButton.enabled = exists

  def __init__(self):
    super(SliceTrackerCaseManagerPlugin, self).__init__()
    self.caseRootDir = self.getSetting('CasesRootLocation', self.MODULE_NAME)

  def clearData(self):
    self.update()

  def setupIcons(self):
    self.newIcon = self.createIcon('icon-new.png')
    self.openIcon = self.createIcon('icon-open.png')
    self.closeIcon = self.createIcon('icon-close.png')
    self.completeIcon = self.createIcon('icon-complete.png')

  def setup(self):
    iconSize = qt.QSize(36, 36)
    self.createNewCaseButton = self.createButton("", icon=self.newIcon, iconSize=iconSize, toolTip="Start a new case")
    self.openCaseButton = self.createButton("", icon=self.openIcon, iconSize=iconSize, toolTip="Open case")
    self.closeCaseButton = self.createButton("", icon=self.closeIcon, iconSize=iconSize,
                                             toolTip="Close case with resume support", enabled=False)
    self.completeCaseButton = self.createButton("", icon=self.completeIcon, iconSize=iconSize, enabled=False,
                                                toolTip="Close case and mark as completed (no resume supported)")
    self.setupCaseWatchBox()
    self.casesRootDirectoryButton = self.createDirectoryButton(text="Choose cases root location",
                                                               caption="Choose cases root location",
                                                               directory=self.getSetting('CasesRootLocation',
                                                                                         self.MODULE_NAME))
    self.caseDirectoryInformationArea = ctk.ctkCollapsibleButton()
    self.caseDirectoryInformationArea.collapsed = True
    self.caseDirectoryInformationArea.text = "Directory Settings"
    self.directoryConfigurationLayout = qt.QGridLayout(self.caseDirectoryInformationArea)
    self.directoryConfigurationLayout.addWidget(qt.QLabel("Cases Root Directory"), 1, 0, 1, 1)
    self.directoryConfigurationLayout.addWidget(self.casesRootDirectoryButton, 1, 1, 1, 1)
    self.directoryConfigurationLayout.addWidget(self.caseWatchBox, 2, 0, 1, qt.QSizePolicy.ExpandFlag)

    self.caseGroupBox = qt.QGroupBox("Case")
    self.caseGroupBoxLayout = qt.QFormLayout(self.caseGroupBox)
    self.caseGroupBoxLayout.addWidget(self.createHLayout([self.createNewCaseButton, self.openCaseButton,
                                                          self.closeCaseButton, self.completeCaseButton]))
    self.caseGroupBoxLayout.addWidget(self.caseDirectoryInformationArea)
    self.layout().addWidget(self.caseGroupBox)

  def setupCaseWatchBox(self):
    watchBoxInformation = [WatchBoxAttribute('CurrentCaseDirectory', 'Directory'),
                           WatchBoxAttribute('CurrentPreopDICOMDirectory', 'Preop DICOM Directory: '),
                           WatchBoxAttribute('CurrentIntraopDICOMDirectory', 'Intraop DICOM Directory: '),
                           WatchBoxAttribute('mpReviewDirectory', 'mpReview Directory: ')]
    self.caseWatchBox = BasicInformationWatchBox(watchBoxInformation, title="Current Case")

  def setupConnections(self):
    self.createNewCaseButton.clicked.connect(self.onCreateNewCaseButtonClicked)
    self.openCaseButton.clicked.connect(self.onOpenCaseButtonClicked)
    self.closeCaseButton.clicked.connect(self.onCloseCaseButtonClicked)
    self.completeCaseButton.clicked.connect(self.onCompleteCaseButtonClicked)
    self.casesRootDirectoryButton.directoryChanged.connect(lambda: setattr(self, "caseRootDir",
                                                                           self.casesRootDirectoryButton.directory))

  def onCreateNewCaseButtonClicked(self):
    if not self.checkAndWarnUserIfCaseInProgress():
      return
    self.caseDialog = NewCaseSelectionNameWidget(self.caseRootDir)
    selectedButton = self.caseDialog.exec_()
    if selectedButton == qt.QMessageBox.Ok:
      self.session.createNewCase(self.caseDialog.newCaseDirectory)

  def onOpenCaseButtonClicked(self):
    if not self.checkAndWarnUserIfCaseInProgress():
      return
    self.session.directory = qt.QFileDialog.getExistingDirectory(self.parent().window(), "Select Case Directory",
                                                                 self.caseRootDir)

  def onCloseCaseButtonClicked(self):
    self.session.close(save=slicer.util.confirmYesNoDisplay("Save the case data?", title="Close Case",
                                                            windowTitle="SliceTracker"))

  def onCompleteCaseButtonClicked(self):
    self.session.complete()

  @logmethod(logging.INFO)
  def onNewCaseStarted(self, caller, event):
    self.update()

  @logmethod(logging.INFO)
  def onCaseOpened(self, caller, event):
    self.update()

  def update(self):
    self.updateCaseButtons()
    self.updateCaseWatchBox()

  @vtk.calldata_type(vtk.VTK_STRING)
  def onCaseClosed(self, caller, event, callData):
    self.clearData()

  def onLoadingMetadataSuccessful(self, caller, event):
    self.updateCaseButtons()

  def updateCaseWatchBox(self):
    if not self.session.isRunning():
      self.caseWatchBox.reset()
      return
    self.caseWatchBox.setInformation("CurrentCaseDirectory", os.path.relpath(self.session.directory, self.caseRootDir),
                                     toolTip=self.session.directory)
    self.caseWatchBox.setInformation("CurrentPreopDICOMDirectory", os.path.relpath(self.session.preopDICOMDirectory,
                                                                                   self.caseRootDir),
                                     toolTip=self.session.preopDICOMDirectory)
    self.caseWatchBox.setInformation("CurrentIntraopDICOMDirectory", os.path.relpath(self.session.intraopDICOMDirectory,
                                                                                     self.caseRootDir),
                                     toolTip=self.session.intraopDICOMDirectory)
    self.caseWatchBox.setInformation("mpReviewDirectory", os.path.relpath(self.session.preprocessedDirectory,
                                                                          self.caseRootDir),
                                     toolTip=self.session.preprocessedDirectory)

  def updateCaseButtons(self):
    self.closeCaseButton.enabled = self.session.directory is not None
    self.completeCaseButton.enabled = self.session.directory is not None

  def checkAndWarnUserIfCaseInProgress(self):
    if self.session.isRunning():
      if not slicer.util.confirmYesNoDisplay("Current case will be closed. Do you want to proceed?"):
        return False
    return True