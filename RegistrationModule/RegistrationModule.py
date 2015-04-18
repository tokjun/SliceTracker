import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Editor import EditorWidget
from EditorLib import EditColor
import Editor
from EditorLib import EditUtil
from EditorLib import EditorLib


#
# RegistrationModule
#

class RegistrationModule(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RegistrationModule"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Peter Behringer (SPL), Andriy Fedorov (SPL)"]
    self.parent.helpText = """ Module for easy registration. """
    self.parent.acknowledgementText = """SPL, Brigham & Womens""" # replace with organization, grant and thanks.

#
# RegistrationModuleWidget
#

class RegistrationModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Parameters
    self.settings = qt.QSettings()
    self.temp = None
    self.updatePatientSelectorFlag = True
    self.warningFlag = False
    self.patientNames = []
    self.patientIDs = []
    self.addedPatients = []

    self.markupsLogic=slicer.modules.markups.logic()

    layoutManager=slicer.app.layoutManager()

    # set Compare Screen
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)

    # set Axial Views only
    redWidget = layoutManager.sliceWidget('Red')
    yellowWidget = layoutManager.sliceWidget('Yellow')
    redLogic=redWidget.sliceLogic()
    yellowLogic=yellowWidget.sliceLogic()
    sliceNodeRed=redLogic.GetSliceNode()
    sliceNodeYellow=yellowLogic.GetSliceNode()
    sliceNodeRed.SetOrientationToAxial()
    sliceNodeYellow.SetOrientationToAxial()

    """
    moduleDir = os.path.dirname(self.parent.path)
    print ('moduleDir = '+moduleDir)
    """

    # create Patient WatchBox

    self.patientViewBox=qt.QGroupBox()
    self.patientViewBox.setStyleSheet('background-color: rgb(230,230,230)')
    self.patientViewBox.setFixedHeight(80)
    self.patientViewBoxLayout=qt.QGridLayout()
    self.patientViewBox.setLayout(self.patientViewBoxLayout)
    self.patientViewBoxLayout.setColumnMinimumWidth(1,50)
    self.patientViewBoxLayout.setColumnMinimumWidth(2,50)
    self.patientViewBoxLayout.setHorizontalSpacing(0)
    self.layout.addWidget(self.patientViewBox)

    self.kategoryPatientID=qt.QLabel()
    self.kategoryPatientID.setText('Patient ID: ')
    self.patientViewBoxLayout.addWidget(self.kategoryPatientID,1,1)

    self.kategoryPatientName=qt.QLabel()
    self.kategoryPatientName.setText('Patient Name: ')
    self.patientViewBoxLayout.addWidget(self.kategoryPatientName,2,1)

    self.kategoryPatientBirthDate=qt.QLabel()
    self.kategoryPatientBirthDate.setText('Date of Birth: ')
    self.patientViewBoxLayout.addWidget(self.kategoryPatientBirthDate,3,1)

    self.kategoryStudyDate=qt.QLabel()
    self.kategoryStudyDate.setText('Date of Study:')
    self.patientViewBoxLayout.addWidget(self.kategoryStudyDate,4,1)

    self.patientID=qt.QLabel()
    self.patientID.setText('None')
    self.patientViewBoxLayout.addWidget(self.patientID,1,2)

    self.patientName=qt.QLabel()
    self.patientName.setText('None')
    self.patientViewBoxLayout.addWidget(self.patientName,2,2)

    self.patientBirthDate=qt.QLabel()
    self.patientBirthDate.setText('None')
    self.patientViewBoxLayout.addWidget(self.patientBirthDate,3,2)

    self.studyDate=qt.QLabel()
    self.studyDate.setText('None')
    self.patientViewBoxLayout.addWidget(self.studyDate,4,2)


    # create TabWidget
    self.tabWidget=qt.QTabWidget()
    self.layout.addWidget(self.tabWidget)

    # get the TabBar
    self.tabBar=self.tabWidget.childAt(1,1)

    # create Widgets inside each tab
    self.dataSelectionGroupBox=qt.QGroupBox()
    self.labelSelectionGroupBox=qt.QGroupBox()
    self.registrationGroupBox=qt.QGroupBox()
    self.evaluationGroupBox=qt.QGroupBox()

    # set up PixMaps
    self.dataSelectionIconPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-dataselection_fit.png')
    self.labelSelectionIconPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-labelselection_fit.png')
    self.registrationSectionPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-registration_fit.png')
    self.evaluationSectionPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-evaluation_fit.png')
    self.newImageDataPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-newImageData.png')

    # set up Icons
    self.dataSelectionIcon=qt.QIcon(self.dataSelectionIconPixmap)
    self.labelSelectionIcon=qt.QIcon(self.labelSelectionIconPixmap)
    self.registrationSectionIcon=qt.QIcon(self.registrationSectionPixmap)
    self.evaluationSectionIcon=qt.QIcon(self.evaluationSectionPixmap)
    self.newImageDataIcon=qt.QIcon(self.newImageDataPixmap)

    # set up Icon Size
    size=qt.QSize()
    size.setHeight(50)
    size.setWidth(110)
    self.tabWidget.setIconSize(size)

    # create Layout for each groupBox
    self.dataSelectionGroupBoxLayout=qt.QFormLayout()
    self.labelSelectionGroupBoxLayout=qt.QFormLayout()
    self.registrationGroupBoxLayout=qt.QFormLayout()
    self.evaluationGroupBoxLayout=qt.QFormLayout()

    # set Layout
    self.dataSelectionGroupBox.setLayout(self.dataSelectionGroupBoxLayout)
    self.labelSelectionGroupBox.setLayout(self.labelSelectionGroupBoxLayout)
    self.registrationGroupBox.setLayout(self.registrationGroupBoxLayout)
    self.evaluationGroupBox.setLayout(self.evaluationGroupBoxLayout)

    # add Tabs
    self.tabWidget.addTab(self.dataSelectionGroupBox,self.dataSelectionIcon,'')
    self.tabWidget.addTab(self.labelSelectionGroupBox,self.labelSelectionIcon,'')
    self.tabWidget.addTab(self.registrationGroupBox,self.registrationSectionIcon,'')
    self.tabWidget.addTab(self.evaluationGroupBox,self.evaluationSectionIcon,'')

    # TODO: set window layout for every step
    # self.tabWidget.currentIndex returns current user Tab position
    self.tabWidget.connect('currentChanged(int)',self.tabWidgetClicked)


    # TODO: Integrate icons into Resources folder and add them to CMAKE file

    # Set Layout
    lm=slicer.app.layoutManager()
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)


    #
    # Step 1: Data Selection
    #

    # Layout within a row of that section
    selectPatientRowLayout = qt.QHBoxLayout()

    # Create PatientSelector
    self.patientSelector=ctk.ctkComboBox()
    self.patientSelector.connect('currentIndexChanged(int)',self.updatePatientViewBox)
    selectPatientRowLayout.addWidget(self.patientSelector)
    self.dataSelectionGroupBoxLayout.addRow("Choose Patient ID: ", selectPatientRowLayout)

    # fill PatientSelector with Patients that are currently in slicer.dicomDatabase
    db = slicer.dicomDatabase
    db.connect('databaseChanged()', self.updatePatientSelector)

    # Folder Button
    folderPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-folder.png')
    folderIcon=qt.QIcon(folderPixmap)


    # Preop Directory Button
    self.preopDirButton = qt.QPushButton(str(self.settings.value('RegistrationModule/PreopLocation')))
    self.preopDirButton.connect('clicked()', self.onPreopDirSelected)
    self.preopDirButton.setIcon(folderIcon)
    self.dataSelectionGroupBoxLayout.addRow("Select preop directory:", self.preopDirButton)


    # Intraop Directory Button
    self.intraopDirButton = qt.QPushButton(str(self.settings.value('RegistrationModule/PreopLocation')))
    self.intraopDirButton.connect('clicked()', self.onIntraopDirSelected)
    self.intraopDirButton.setIcon(folderIcon)
    self.dataSelectionGroupBoxLayout.addRow("Select intraop directory:", self.intraopDirButton)

    # add buffer line
    self.layout.addStretch(1)

    # SERIES SELECTION
    self.step3frame = ctk.ctkCollapsibleGroupBox()
    self.step3frame.setTitle("Intraop Series")
    self.dataSelectionGroupBoxLayout.addRow(self.step3frame)
    step3Layout = qt.QFormLayout(self.step3frame)

    # create ListView for intraop series selection
    self.seriesView = qt.QListView()
    self.seriesView.setObjectName('SeriesTable')
    self.seriesView.setSpacing(3)
    self.seriesModel = qt.QStandardItemModel()
    self.seriesModel.setHorizontalHeaderLabels(['Series ID'])
    self.seriesView.setModel(self.seriesModel)
    self.seriesView.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)
    self.seriesView.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
    step3Layout.addWidget(self.seriesView)

    # Load Series into Slicer Button
    self.loadIntraopDataButton = qt.QPushButton("Load and Segment")
    self.loadIntraopDataButton.toolTip = "Load and Segment"
    self.loadIntraopDataButton.enabled = True
    self.dataSelectionGroupBoxLayout.addWidget(self.loadIntraopDataButton)

    # Simulate DICOM Income 2
    self.simulateDataIncomeButton2 = qt.QPushButton("Simulate AMIGO Data Income 1")
    self.simulateDataIncomeButton2.toolTip = ("Simulate Data Income 1: Localizer, COVER TEMPLATE, NEEDLE GUIDANCE 3")
    self.simulateDataIncomeButton2.enabled = True
    self.simulateDataIncomeButton2.setStyleSheet('background-color: rgb(255,102,0)')
    self.dataSelectionGroupBoxLayout.addWidget(self.simulateDataIncomeButton2)

    # Simulate DICOM Income 3
    self.simulateDataIncomeButton3 = qt.QPushButton("Simulate AMIGO Data Income 2")
    self.simulateDataIncomeButton3.toolTip = ("Simulate Data Income 2")
    self.simulateDataIncomeButton3.enabled = True
    self.simulateDataIncomeButton3.setStyleSheet('background-color: rgb(255,102,0)')
    self.dataSelectionGroupBoxLayout.addWidget(self.simulateDataIncomeButton3)

    # Simulate DICOM Income 4
    self.simulateDataIncomeButton4 = qt.QPushButton("Simulate AMIGO Data Income 3")
    self.simulateDataIncomeButton4.toolTip = ("Simulate Data Income 3")
    self.simulateDataIncomeButton4.enabled = True
    self.simulateDataIncomeButton4.setStyleSheet('background-color: rgb(255,102,0)')
    self.dataSelectionGroupBoxLayout.addWidget(self.simulateDataIncomeButton4)

    # Load Series into Slicer Button
    self.updateAnnotationButton = qt.QPushButton("Update Annotation")
    self.updateAnnotationButton.toolTip = "Load and Segment"
    self.updateAnnotationButton.enabled = True
    self.dataSelectionGroupBoxLayout.addWidget(self.updateAnnotationButton)
    self.updateAnnotationButton.connect('clicked(bool)',self.updateAnnotationDisplays)

    #
    # Step 2: Label Selection
    #


    self.labelSelectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.labelSelectionCollapsibleButton.text = "Step 2: Label Selection"
    self.labelSelectionCollapsibleButton.collapsed=0
    self.labelSelectionCollapsibleButton.hide()
    self.layout.addWidget(self.labelSelectionCollapsibleButton)



    #
    # preop label selector
    #

    self.preopLabelSelector = slicer.qMRMLNodeComboBox()
    self.preopLabelSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.preopLabelSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.preopLabelSelector.selectNodeUponCreation = True
    self.preopLabelSelector.addEnabled = False
    self.preopLabelSelector.removeEnabled = False
    self.preopLabelSelector.noneEnabled = False
    self.preopLabelSelector.showHidden = False
    self.preopLabelSelector.showChildNodeTypes = False
    self.preopLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.preopLabelSelector.setToolTip( "Pick the input to the algorithm." )
    self.labelSelectionGroupBoxLayout.addRow("Preop Image label: ", self.preopLabelSelector)

    #
    # reference volume selector
    #

    self.referenceVolumeSelector = slicer.qMRMLNodeComboBox()
    self.referenceVolumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.referenceVolumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.referenceVolumeSelector.selectNodeUponCreation = True
    self.referenceVolumeSelector.addEnabled = False
    self.referenceVolumeSelector.removeEnabled = False
    self.referenceVolumeSelector.noneEnabled = True
    self.referenceVolumeSelector.showHidden = False
    self.referenceVolumeSelector.showChildNodeTypes = False
    self.referenceVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.referenceVolumeSelector.setToolTip( "Pick the input to the algorithm." )
    self.referenceVolumeSelector.connect('currentNodeChanged(bool)',self.onTab2clicked)
    self.labelSelectionGroupBoxLayout.addRow("Reference Volume: ", self.referenceVolumeSelector)

    # Set Icon Size for the 4 Icon Items
    size=qt.QSize(60,60)

    # Create Quick Segmentation Button
    pixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-quickSegmentation.png')
    icon=qt.QIcon(pixmap)
    self.startQuickSegmentationButton=qt.QPushButton()
    self.startQuickSegmentationButton.setIcon(icon)
    self.startQuickSegmentationButton.setIconSize(size)
    self.startQuickSegmentationButton.setFixedHeight(70)
    self.startQuickSegmentationButton.setFixedWidth(70)
    self.startQuickSegmentationButton.setStyleSheet("background-color: rgb(255,255,255)")


    # Create Label Segmentation Button
    pixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-labelSegmentation.png')
    icon=qt.QIcon(pixmap)
    self.startLabelSegmentationButton=qt.QPushButton()
    self.startLabelSegmentationButton.setIcon(icon)
    self.startLabelSegmentationButton.setIconSize(size)
    self.startLabelSegmentationButton.setFixedHeight(70)
    self.startLabelSegmentationButton.setFixedWidth(70)
    self.startLabelSegmentationButton.setStyleSheet("background-color: rgb(255,255,255)")


    # Create Apply Segmentation Button
    pixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-applySegmentation.png')
    icon=qt.QIcon(pixmap)
    self.applySegmentationButton=qt.QPushButton()
    self.applySegmentationButton.setIcon(icon)
    self.applySegmentationButton.setIconSize(size)
    self.applySegmentationButton.setFixedHeight(70)
    self.applySegmentationButton.setFixedWidth(70)
    self.applySegmentationButton.setStyleSheet("background-color: rgb(255,255,255)")
    self.applySegmentationButton.setEnabled(0)

    # Create ButtonBox to fill in those Buttons
    buttonBox1=qt.QDialogButtonBox()
    buttonBox1.addButton(self.applySegmentationButton,buttonBox1.ActionRole)
    buttonBox1.addButton(self.startQuickSegmentationButton,buttonBox1.ActionRole)
    buttonBox1.addButton(self.startLabelSegmentationButton,buttonBox1.ActionRole)
    buttonBox1.setLayoutDirection(1)
    buttonBox1.centerButtons=False
    self.labelSelectionGroupBoxLayout.addWidget(buttonBox1)

    # connections

    self.startQuickSegmentationButton.connect('clicked(bool)',self.onStartSegmentationButton)
    self.startLabelSegmentationButton.connect('clicked(bool)',self.onStartLabelSegmentationButton)
    self.applySegmentationButton.connect('clicked(bool)',self.onApplySegmentationButton)
    self.simulateDataIncomeButton2.connect('clicked(bool)',self.onsimulateDataIncomeButton2)
    self.simulateDataIncomeButton3.connect('clicked(bool)',self.onsimulateDataIncomeButton3)
    self.simulateDataIncomeButton4.connect('clicked(bool)',self.onsimulateDataIncomeButton4)


    #
    # Editor Widget
    #


    self.editUtil = EditorLib.EditUtil.EditUtil()
    editorWidgetParent = slicer.qMRMLWidget()
    editorWidgetParent.setLayout(qt.QVBoxLayout())
    editorWidgetParent.setMRMLScene(slicer.mrmlScene)

    self.editorWidget = EditorWidget(parent=editorWidgetParent,showVolumesFrame=False)
    self.editorWidget.setup()
    self.editorParameterNode = self.editUtil.getParameterNode()
    self.labelSelectionGroupBoxLayout.addRow(editorWidgetParent)


    # connections

    self.loadIntraopDataButton.connect('clicked(bool)',self.loadSeriesIntoSlicer)
    self.loadIntraopDataButton.connect('clicked(bool)',self.loadSeriesIntoSlicer)



    #
    # Step 3: Registration
    #


    #
    # preop volume selector
    #

    self.preopVolumeSelector = slicer.qMRMLNodeComboBox()
    self.preopVolumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.preopVolumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.preopVolumeSelector.selectNodeUponCreation = True
    self.preopVolumeSelector.addEnabled = False
    self.preopVolumeSelector.removeEnabled = False
    self.preopVolumeSelector.noneEnabled = False
    self.preopVolumeSelector.showHidden = False
    self.preopVolumeSelector.showChildNodeTypes = False
    self.preopVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.preopVolumeSelector.setToolTip( "Pick the input to the algorithm." )
    self.registrationGroupBoxLayout.addRow("Preop Image Volume: ", self.preopVolumeSelector)

    #
    # preop label selector
    #

    self.preopLabelSelector = slicer.qMRMLNodeComboBox()
    self.preopLabelSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.preopLabelSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.preopLabelSelector.selectNodeUponCreation = False
    self.preopLabelSelector.addEnabled = False
    self.preopLabelSelector.removeEnabled = False
    self.preopLabelSelector.noneEnabled = False
    self.preopLabelSelector.showHidden = False
    self.preopLabelSelector.showChildNodeTypes = False
    self.preopLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.preopLabelSelector.setToolTip( "Pick the input to the algorithm." )
    self.registrationGroupBoxLayout.addRow("Preop Label Volume: ", self.preopLabelSelector)

    #
    # intraop volume selector
    #

    self.intraopVolumeSelector = slicer.qMRMLNodeComboBox()
    self.intraopVolumeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.intraopVolumeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.intraopVolumeSelector.selectNodeUponCreation = True
    self.intraopVolumeSelector.addEnabled = False
    self.intraopVolumeSelector.removeEnabled = False
    self.intraopVolumeSelector.noneEnabled = True
    self.intraopVolumeSelector.showHidden = False
    self.intraopVolumeSelector.showChildNodeTypes = False
    self.intraopVolumeSelector.setMRMLScene( slicer.mrmlScene )
    self.intraopVolumeSelector.setToolTip( "Pick the input to the algorithm." )
    self.registrationGroupBoxLayout.addRow("Intraop Image Volume: ", self.intraopVolumeSelector)

    #
    # intraop label selector
    #

    self.intraopLabelSelector = slicer.qMRMLNodeComboBox()
    self.intraopLabelSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.intraopLabelSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.intraopLabelSelector.selectNodeUponCreation = True
    self.intraopLabelSelector.addEnabled = False
    self.intraopLabelSelector.removeEnabled = False
    self.intraopLabelSelector.noneEnabled = False
    self.intraopLabelSelector.showHidden = False
    self.intraopLabelSelector.showChildNodeTypes = False
    self.intraopLabelSelector.setMRMLScene( slicer.mrmlScene )
    self.intraopLabelSelector.setToolTip( "Pick the input to the algorithm." )
    self.intraopLabelSelector.setToolTip( "Pick the input to the algorithm." )
    self.registrationGroupBoxLayout.addRow("Intraop Label Volume: ", self.intraopLabelSelector)



    #
    # fiducial node selector
    #

    self.fiducialSelector = slicer.qMRMLNodeComboBox()
    self.fiducialSelector.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.fiducialSelector.selectNodeUponCreation = False
    self.fiducialSelector.addEnabled = False
    self.fiducialSelector.removeEnabled = False
    self.fiducialSelector.noneEnabled = True
    self.fiducialSelector.showHidden = False
    self.fiducialSelector.showChildNodeTypes = False
    self.fiducialSelector.setMRMLScene( slicer.mrmlScene )
    self.fiducialSelector.setToolTip( "Select the Targets" )
    self.registrationGroupBoxLayout.addRow("Targets: ", self.fiducialSelector)



    # connections for refreshing:

    self.preopVolumeSelector.connect('currentNodeChanged(bool)',self.onTab3clicked)
    self.intraopVolumeSelector.connect('currentNodeChanged(bool)',self.onTab3clicked)
    self.intraopLabelSelector.connect('currentNodeChanged(bool)',self.onTab3clicked)
    self.preopLabelSelector.connect('currentNodeChanged(bool)',self.onTab3clicked)
    self.fiducialSelector.connect('currentNodeChanged(bool)',self.onTab3clicked)

    #
    # Apply Affine Registration
    #



    greenCheckPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-greenCheck.png')
    greenCheckIcon=qt.QIcon(greenCheckPixmap)
    self.applyRegistrationButton = qt.QPushButton("Apply Registration")
    self.applyRegistrationButton.setIcon(greenCheckIcon)
    self.applyRegistrationButton.toolTip = "Run the algorithm."
    self.applyRegistrationButton.enabled = True
    self.applyRegistrationButton.setFixedHeight(45)
    self.registrationGroupBoxLayout.addRow(self.applyRegistrationButton)
    self.applyRegistrationButton.connect('clicked(bool)',self.applyRegistration)



    #
    # Load and Set Data
    #

    self.loadAndSetDataButton = qt.QPushButton("load And Set data")
    self.loadAndSetDataButton.toolTip = "Run the algorithm."
    self.loadAndSetDataButton.enabled = True
    self.loadAndSetDataButton.setStyleSheet('background-color: rgb(255,102,0)')
    self.registrationGroupBoxLayout.addRow(self.loadAndSetDataButton)
    self.loadAndSetDataButton.connect('clicked(bool)',self.loadAndSetdata)

    #
    # Step 4: Registration Evaluation
    #

    # Show Rigid Registration
    self.rigidCheckBox=qt.QCheckBox()
    self.rigidCheckBox.setText('Show Rigid Registration')
    self.rigidCheckBox.connect('clicked(bool)',self.onRigidCheckBoxClicked)

    # Show Rigid Registration
    self.affineCheckBox=qt.QCheckBox()
    self.affineCheckBox.setText('Show Affine Registration')
    self.affineCheckBox.setChecked(1)
    self.affineCheckBox.connect('clicked(bool)',self.onAffineCheckBoxClicked)

    # Show Rigid Registration
    self.bsplineCheckBox=qt.QCheckBox()
    self.bsplineCheckBox.setText('Show BSpline Registration')
    self.bsplineCheckBox.connect('clicked(bool)',self.onBSplineCheckBoxClicked)

    # Show Rigid Registration
    self.targetCheckBox=qt.QCheckBox()
    self.targetCheckBox.setText('Show Transformed Targets')
    self.targetCheckBox.setChecked(1)
    self.targetCheckBox.connect('clicked(bool)',self.onTargetCheckBox)

    # Add widgets to layout
    self.evaluationGroupBoxLayout.addWidget(self.rigidCheckBox)
    self.evaluationGroupBoxLayout.addWidget(self.affineCheckBox)
    self.evaluationGroupBoxLayout.addWidget(self.bsplineCheckBox)
    self.evaluationGroupBoxLayout.addWidget(self.targetCheckBox)

    # create Slider
    control = qt.QWidget()
    self.opacitySlider = qt.QSlider(qt.Qt.Horizontal,control)
    self.opacitySlider.connect('valueChanged(int)', self.changeOpacity)
    self.opacitySlider.setObjectName("opacitySlider")
    self.opacitySlider.setMaximum(100)
    self.opacitySlider.setMinimum(0)
    self.opacitySlider.setValue(100)
    self.opacitySlider.setMaximumWidth(200)
    self.evaluationGroupBoxLayout.addWidget(self.opacitySlider)

    # Save Data Button
    littleDiscPixmap=qt.QPixmap('/Users/peterbehringer/MyDevelopment/Icons/icon-littleDisc.png')
    littleDiscIcon=qt.QIcon(littleDiscPixmap)
    self.saveDataButton=qt.QPushButton('Save Data')
    self.saveDataButton.setMaximumWidth(150)
    self.saveDataButton.setIcon(littleDiscIcon)

    self.evaluationGroupBoxLayout.addWidget(self.saveDataButton)

    # DEBUG: prepare IntraopFolder for tests
    self.removeEverythingInIntraopTestFolder()

    # enter Module on Tab 1
    self.onTab1clicked()

    # self.updateAnnotationDisplays()



  def newAnnotation(self):


    self.layoutManager = slicer.app.layoutManager()

    redWidget = self.layoutManager.sliceWidget('Red')
    redLogic=redWidget.sliceLogic()

    backgroundLayer = redLogic.GetBackgroundLayer()
    sliceNode = backgroundLayer.GetSliceNode()
    sliceViewName = sliceNode.GetLayoutName()

    self.renderers = {}

    sliceWidget = self.layoutManager.sliceWidget(sliceViewName)
    sliceView = sliceWidget.sliceView()

    renderWindow = sliceView.renderWindow()
    renderWindow.GetRenderers()
    renderer = renderWindow.GetRenderers().GetItemAsObject(0)
    self.renderers[sliceViewName] = renderer

    sliceViewName = sliceNode.GetLayoutName()

    textActor = vtk.vtkTextActor()
    textActor.SetInput("PREOP")
    textProperty = textActor.GetTextProperty()

    # set font size
    textProperty.SetFontSize(40)
    textProperty.SetBold(1)

    """
    # set font family
    if self.fontFamily == 'Times':
      textProperty.SetFontFamilyToTimes()
    else:
      textProperty.SetFontFamilyToArial()
    """

    # set ruler text actor position

    redWidget = self.layoutManager.sliceWidget('Red')
    sliceView = redWidget.sliceView()

    viewWidth=sliceView.width

    print ('viewWidth = '+ str(viewWidth))
    print str(int(0.5*viewWidth))

    viewHeight=sliceView.height

    print ('viewHeight = '+ str(viewHeight))
    print str(int(0.8*viewHeight))

    textActor.SetDisplayPosition(int(0.5*viewWidth)+300,int(0.8*viewHeight)+800)

    #renderer.AddActor2D(self.scalingRulerActors[sliceViewName])
    renderer.RemoveActor2D(textActor)
    renderer.AddActor2D(textActor)

  def removeEverythingInIntraopTestFolder(self):
    cmd="rm -rfv /Users/peterbehringer/MyImageData/A_INTRAOP_DIR/*"
    os.system(cmd)

  def onPreopDirSelected(self):
    self.preopDataDir = qt.QFileDialog.getExistingDirectory(self.parent,'Preop data directory', '/Users/peterbehringer/MyImageData/A_PREOP_DIR')
    self.preopDirButton.text = self.preopDataDir
    self.settings.setValue('RegistrationModule/PreopLocation', self.preopDataDir)
    print('Directory selected:')
    print(self.preopDataDir)
    print(self.settings.value('RegistrationModule/PreopLocation'))
    self.loadPreopData()

  def onIntraopDirSelected(self):
    self.intraopDataDir = qt.QFileDialog.getExistingDirectory(self.parent,'Intraop data directory', '/Users/peterbehringer/MyImageData/A_INTRAOP_DIR/')
    self.intraopDirButton.text = self.intraopDataDir
    self.settings.setValue('RegistrationModule/IntraopLocation', self.intraopDataDir)

    # DEBUG:
    # self.deleteEverythingInIntraopFolder()

    print('Directory selected:')
    print(self.intraopDataDir)
    print(self.settings.value('RegistrationModule/IntraopLocation'))

    print ('Now initialize listener')
    if self.intraopDataDir != None:
      self.initializeListener()

  def enterLabelSelectionSection(self):

    self.tabWidget.setCurrentIndex(1)


    # Get SliceWidgets
    lm=slicer.app.layoutManager()
    redWidget = lm.sliceWidget('Red')
    compositNodeRed = redWidget.mrmlSliceCompositeNode()

    # set Layout to redSliceViewOnly for segmentation
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

    # Hide Labels
    compositNodeRed.SetLabelOpacity(0)

    # clear current Label
    compositNodeRed.SetLabelVolumeID(None)

    # hide preop Fiducials



    # TODO:ggg
    # left side: show imported new Intraop Image as Reference

    # set Reference Volume -> new Intraop Image

    # right side:

    # show preop T2-Image

    # show segmentation label

    # show contours only

  def tabWidgetClicked(self):

    if self.tabWidget.currentIndex==0:
      self.onTab1clicked()

        # set up window mode

    if self.tabWidget.currentIndex==1:
      self.onTab2clicked()

        # show reference image

    if self.tabWidget.currentIndex==2:
      self.onTab3clicked()
    if self.tabWidget.currentIndex==3:
      self.onTab4clicked()

  def onTab1clicked(self):

    # set the standard Icon
    self.tabBar.setTabIcon(0,self.dataSelectionIcon)

    # grab the settings from last session
    settings = qt.QSettings()

    # update the patients in patient selector
    self.updatePatientSelector()

    preopLocation = settings.value('RegistrationModule/PreopLocation')
    intraopLocation = settings.value('RegistrationModule/IntraopLocation')
    outputLocation = settings.value('RegistrationModule/OutputLocation')


    # SCREEN SETUP
    # =========================================================================



    # =========================================================================

  def onTab2clicked(self):

    # ensure, that reference volume is set before making buttons clickable
    if self.referenceVolumeSelector.currentNode() == None:
      self.startLabelSegmentationButton.setEnabled(0)
      self.startQuickSegmentationButton.setEnabled(0)

    else:
      self.startLabelSegmentationButton.setEnabled(1)
      self.startQuickSegmentationButton.setEnabled(1)




    print 'on Tab 2 clicked'

  def onTab3clicked(self):

    # check, that Input is set
    if self.preopVolumeSelector.currentNode() != None and self.intraopVolumeSelector.currentNode() != None and self.preopLabelSelector.currentNode() != None and self.intraopLabelSelector.currentNode() != None and self.fiducialSelector.currentNode() != None:
      self.applyRegistrationButton.setEnabled(1)
    else:
      self.applyRegistrationButton.setEnabled(0)

  def onTab4clicked(self):
    print 'on Tab 4 clicked'

  def updatePatientSelector(self):

    if self.updatePatientSelectorFlag:

      db = slicer.dicomDatabase
      indexer = ctk.ctkDICOMIndexer()

      # check current patients and patient ID's in the slicer.dicomDatabase
      if db.patients()==None:
        self.patientSelector.addItem('None patient found')

      for patient in db.patients():
        for study in db.studiesForPatient(patient):
          for series in db.seriesForStudy(study):
            for file in db.filesForSeries(series):

               indexer.addFile(db,file,None)
               if db.fileValue(file,'0010,0010') not in self.patientNames:
                 self.patientNames.append(slicer.dicomDatabase.fileValue(file,'0010,0010'))

               if slicer.dicomDatabase.fileValue(file,'0010,0020') not in self.patientIDs:
                 self.patientIDs.append(slicer.dicomDatabase.fileValue(file,'0010,0020'))

      # add patientNames and patientIDs to patientSelector
      for patient in self.patientIDs:
       if patient not in self.addedPatients:
        self.patientSelector.addItem(patient)
        self.addedPatients.append(patient)
       else:
         pass

  def infoPopup(self,message):
    messageBox = qt.QMessageBox()
    messageBox.information(None, 'RegistrationModule', message)

  def updatePatientViewBox(self):

    if self.patientSelector.currentIndex != None:

      self.currentPatientName=None
      # get the current index from patientSelector comboBox
      currentIndex=self.patientSelector.currentIndex

      # get the current patient ID
      self.currentID=self.patientIDs[currentIndex]

      # initialize dicomDatabase
      db = slicer.dicomDatabase

      # looking for currentPatientName and currentBirthDate
      for patient in db.patients():
        for study in db.studiesForPatient(patient):
          for series in db.seriesForStudy(study):
            for file in db.filesForSeries(series):

               if db.fileValue(file,'0010,00020') == self.currentID:
                 currentPatientNameDicom= db.fileValue(file,'0010,0010')
                 try:
                   currentBirthDateDicom = db.fileValue(file,'0010,0030')
                 except:
                   currentBirthDateDicom = None

      if currentBirthDateDicom == None:
        self.patientBirthDate.setText('No Date found')
      else:
        # convert date of birth from 19550112 (yyyymmdd) to 1955-01-12
        currentBirthDateDicom=str(currentBirthDateDicom)
        self.currentBirthDate=currentBirthDateDicom[0:4]+"-"+currentBirthDateDicom[4:6]+"-"+currentBirthDateDicom[6:8]

      # convert patient name from XXXX^XXXX to XXXXX, XXXXX
      if "^" in currentPatientNameDicom:
        length=len(currentPatientNameDicom)
        index=currentPatientNameDicom.index('^')
        self.currentPatientName=currentPatientNameDicom[0:index]+", "+currentPatientNameDicom[index+1:length]

      # get today date
      self.currentStudyDate=qt.QDate().currentDate()

      # update patientViewBox
      try:
        self.patientBirthDate.setText(self.currentBirthDate)
      except:
        pass
      if self.currentPatientName != None:
        self.patientName.setText(self.currentPatientName)
      else:
        self.patientName.setText(currentPatientNameDicom)
        self.currentPatientName=currentPatientNameDicom
      self.patientID.setText(self.currentID)
      self.studyDate.setText(str(self.currentStudyDate))

      # TODO: Set EVALUATION TAB DISABLED AT BEGINNING

  def updateAnnotation(self):
    lm = slicer.app.layoutManager()

    # get SliceWidgets
    rw = lm.sliceWidget('Red')
    rv = rw.sliceView()

    # get sliceViews
    yw=lm.sliceWidget('Yellow')
    yv=yw.sliceView()

    # get renderWindows
    redRenderWindow = rv.renderWindow()
    yellowRenderWindow=yv.renderWindow()

    # get Interactors
    redInteractor = redRenderWindow.GetInteractor()
    yellowInteractor = yellowRenderWindow.GetInteractor()

    # set Texts Actors
    textRed = vtk.vtkTextActor()
    textRed.SetInput('PREOP')
    textPropertyRed = textRed.GetTextProperty()
    textPropertyRed.SetFontSize(10)
    textPropertyRed.SetColor(1,0,0)
    textPropertyRed.SetBold(1)

    textYellow = vtk.vtkTextActor()
    textYellow.SetInput('INTRAOP')
    textPropertyYellow = textYellow.GetTextProperty()
    textPropertyYellow.SetFontSize(10)
    textPropertyYellow.SetColor(1,0,0)
    textPropertyYellow.SetBold(1)

    # set Text Representation
    text_representation = vtk.vtkTextRepresentation()
    xsize = 0.15
    ysize = 0.15
    ypos = 0.05
    text_representation.GetPositionCoordinate().SetValue(0.5-(0.5*xsize), ypos)
    text_representation.GetPosition2Coordinate().SetValue(xsize, ysize)


    # set Text Widgets
    text_widget_red = vtk.vtkTextWidget()
    text_widget_red.SetRepresentation(text_representation)
    text_widget_red.SetInteractor(redInteractor)
    text_widget_red.SetTextActor(textRed)
    text_widget_red.SelectableOff()
    text_widget_red.On()

    text_widget_yellow = vtk.vtkTextWidget()
    text_widget_yellow.SetRepresentation(text_representation)
    text_widget_yellow.SetInteractor(yellowInteractor)
    text_widget_yellow.SetTextActor(textYellow)
    text_widget_yellow.SelectableOff()
    text_widget_yellow.On()


  def updateAnnotationDisplays(self):
    # get SliceWidgets

    rw=self.layout

    self.layoutManager = slicer.app.layoutManager()
    rw = self.layoutManager.sliceWidget('Red')
    yw=self.layoutManager.sliceWidget('Yellow')

    # update the Slice Annotation
    sliceLogicRed = rw.sliceLogic()
    sliceLogicYellow=yw.sliceLogic()


    sliceLogicRed.AddObserver(vtk.vtkCommand.ModifiedEvent,self.updateAnnotation)
    sliceLogicYellow.AddObserver(vtk.vtkCommand.ModifiedEvent,self.updateAnnotation)

    self.updateAnnotation()


    """
    try:
      self.redRenderer.RemoveViewProp(self.cornerAnnotationDisplayRed)
    except:
      pass

    self.rightUpperMessage = 'PREOP'
    self.rightBottomMessage = ""
    self.leftUpperMessage = ""
    self.leftBottomMessage = ""

    # Corner annotation function

    self.cornerAnnotationDisplayRed = vtk.vtkCornerAnnotation()
    self.cornerAnnotationDisplayRed.SetLinearFontScaleFactor(1)
    self.cornerAnnotationDisplayRed.SetNonlinearFontScaleFactor(1)
    self.cornerAnnotationDisplayRed.SetMaximumFontSize(60)
    self.cornerAnnotationDisplayRed.GetTextProperty().SetColor(1,1,1)
    self.cornerAnnotationDisplayRed.GetTextProperty().SetBold(1)
    self.cornerAnnotationDisplayRed.GetTextProperty().SetFontSize(20)
    self.cornerAnnotationDisplayRed.SetPosition(5,5)
    self.cornerAnnotationDisplayRed.SetPosition2(5,5)
    self.cornerAnnotationDisplayRed.SetBoundsOn()



    self.cornerAnnotationDisplayRed.SetText(0,self.leftBottomMessage)
    self.cornerAnnotationDisplayRed.SetText(1,self.rightBottomMessage)
    self.cornerAnnotationDisplayRed.SetText(2,self.leftUpperMessage)
    self.cornerAnnotationDisplayRed.SetText(3,self.rightUpperMessage)
    self.cornerAnnotationDisplayRed.VisibilityOn()


    # Corner annotation function

    self.cornerAnnotationDisplayYellow = vtk.vtkCornerAnnotation()
    self.cornerAnnotationDisplayYellow.SetLinearFontScaleFactor(1)
    self.cornerAnnotationDisplayYellow.SetNonlinearFontScaleFactor(1)
    self.cornerAnnotationDisplayYellow.SetMaximumFontSize(60)
    self.cornerAnnotationDisplayYellow.GetTextProperty().SetColor(1,1,1)
    self.cornerAnnotationDisplayYellow.GetTextProperty().SetBold(1)
    self.cornerAnnotationDisplayYellow.GetTextProperty().SetFontSize(20)
    self.cornerAnnotationDisplayYellow.SetPosition(5,5)
    self.cornerAnnotationDisplayYellow.SetPosition2(5,5)
    self.cornerAnnotationDisplayYellow.UseBoundsOn()

    self.cornerAnnotationDisplayYellow.SetText(0,self.leftBottomMessage)
    self.cornerAnnotationDisplayYellow.SetText(1,self.rightBottomMessage)
    self.cornerAnnotationDisplayYellow.SetText(2,self.leftUpperMessage)
    self.cornerAnnotationDisplayYellow.SetText(3,'INTRAOP')
    self.cornerAnnotationDisplayYellow.VisibilityOn()

    layout=slicer.app.layoutManager()
    self.redRenderer = layout.sliceWidget('Red').sliceView().renderWindow().GetRenderers().GetFirstRenderer()

    self.redRenderer.AddViewProp(self.cornerAnnotationDisplayRed)
    self.redRenderWindow = self.redRenderer.GetRenderWindow()
    self.redRenderWindow.Render()

    self.yellowRenderer = layout.sliceWidget('Yellow').sliceView().renderWindow().GetRenderers().GetFirstRenderer()
    self.yellowRenderer.AddViewProp(self.cornerAnnotationDisplayYellow)
    self.yellowRenderWindow = self.yellowRenderer.GetRenderWindow()
    self.yellowRenderWindow.Render()
    """


  def onBSplineCheckBoxClicked(self):

    if self.bsplineCheckBox.isChecked():

      # uncheck the other Buttons
      self.affineCheckBox.setChecked(0)
      self.rigidCheckBox.setChecked(0)

      # Get SliceWidgets
      layoutManager=slicer.app.layoutManager()

      redWidget = layoutManager.sliceWidget('Red')
      yellowWidget = layoutManager.sliceWidget('Yellow')

      compositNodeRed = redWidget.mrmlSliceCompositeNode()
      compositNodeYellow = yellowWidget.mrmlSliceCompositeNode()

      # Get the Affine Volume Node
      bsplineVolumeNode=slicer.mrmlScene.GetNodesByName('reg-BSpline').GetItemAsObject(0)

      # Get the Intraop Volume Node

      intraopVolumeNode=self.intraopVolumeSelector.currentNode()

      # Red Slice View:

        # Set Foreground: intraop image
      compositNodeRed.SetForegroundVolumeID(bsplineVolumeNode.GetID())
        # Set Background: Affine Image
      compositNodeRed.SetBackgroundVolumeID(intraopVolumeNode.GetID())


      # Yellow Slice View:

        # Set Foreground: Intraop Image + Fidicuals Affine transformed

        # Set Background: -

  def onAffineCheckBoxClicked(self):

    if self.affineCheckBox.isChecked():

      # uncheck the other Buttons
      self.bsplineCheckBox.setChecked(0)
      self.rigidCheckBox.setChecked(0)

      # Get SliceWidgets
      layoutManager=slicer.app.layoutManager()

      redWidget = layoutManager.sliceWidget('Red')
      yellowWidget = layoutManager.sliceWidget('Yellow')

      compositNodeRed = redWidget.mrmlSliceCompositeNode()
      compositNodeYellow = yellowWidget.mrmlSliceCompositeNode()

      # Get the Affine Volume Node
      affineVolumeNode=slicer.mrmlScene.GetNodesByName('reg-Affine').GetItemAsObject(0)

      # Get the Intraop Volume Node

      intraopVolumeNode=self.intraopVolumeSelector.currentNode()

      # Red Slice View:

        # Set Foreground: intraop image
      compositNodeRed.SetForegroundVolumeID(affineVolumeNode.GetID())
        # Set Background: Affine Image
      compositNodeRed.SetBackgroundVolumeID(intraopVolumeNode.GetID())


      # Yellow Slice View:

        # Set Foreground: Intraop Image + Fidicuals Affine transformed

        # Set Background: -

  def onRigidCheckBoxClicked(self):

    if self.rigidCheckBox.isChecked():
      # uncheck the other Buttons
      self.affineCheckBox.setChecked(0)
      self.bsplineCheckBox.setChecked(0)

      # uncheck the other Buttons
      self.bsplineCheckBox.setChecked(0)
      self.affineCheckBox.setChecked(0)

      # Get SliceWidgets
      layoutManager=slicer.app.layoutManager()

      redWidget = layoutManager.sliceWidget('Red')
      yellowWidget = layoutManager.sliceWidget('Yellow')

      compositNodeRed = redWidget.mrmlSliceCompositeNode()
      compositNodeYellow = yellowWidget.mrmlSliceCompositeNode()

      # Get the Affine Volume Node
      rigidVolumeNode=slicer.mrmlScene.GetNodesByName('reg-Rigid').GetItemAsObject(0)

      # Get the Intraop Volume Node

      intraopVolumeNode=self.intraopVolumeSelector.currentNode()

      # Red Slice View:

        # Set Foreground: intraop image
      compositNodeRed.SetForegroundVolumeID(rigidVolumeNode.GetID())
        # Set Background: Affine Image
      compositNodeRed.SetBackgroundVolumeID(intraopVolumeNode.GetID())


      # Yellow Slice View:

        # Set Foreground: Intraop Image + Fidicuals Affine transformed

        # Set Background: -

  def onTargetCheckBox(self):

    fiducialNode=slicer.mrmlScene.GetNodesByName('targets-REG').GetItemAsObject(0)
    if self.targetCheckBox.isChecked():
      self.markupsLogic.SetAllMarkupsVisibility(fiducialNode,1)
    if not self.targetCheckBox.isChecked():
      self.markupsLogic.SetAllMarkupsVisibility(fiducialNode,0)

  def deleteEverythingInIntraopFolder(self):

    # delete all files in intraop folder
    print ('entered deleteEverythingInIntraopFolder')
    # create fileList
    fileList=[]
    for item in os.listdir(self.intraopDataDir):
      fileList.append(item)

    for file in fileList:
     cmd = ('rm -Rf '+str(self.intraopDataDir)+'/'+file)

     print cmd
     os.system(cmd)

  def onsimulateDataIncomeButton2(self):

    # copy DICOM Files into intraop folder
    imagePath= '/Users/peterbehringer/MyImageData/Prostate_TestData_ProstateBx/Case200-2014-12-12/DICOM/Intraop/_SIMULATION_01/'
    intraopPath=self.intraopDataDir
    cmd = ('cp -a '+imagePath+'. '+intraopPath)
    os.system(cmd)

  def onsimulateDataIncomeButton3(self):

    # copy DICOM Files into intraop folder
    imagePath= '/Users/peterbehringer/MyImageData/Prostate_TestData_ProstateBx/Case200-2014-12-12/DICOM/Intraop/_SIMULATION_02/'
    intraopPath=self.intraopDataDir
    cmd = ('cp -a '+imagePath+'. '+intraopPath)
    os.system(cmd)

  def onsimulateDataIncomeButton4(self):

    # copy DICOM Files into intraop folder
    imagePath= '/Users/peterbehringer/MyImageData/Prostate_TestData_ProstateBx/Case200-2014-12-12/DICOM/Intraop/_SIMULATION_03/'
    intraopPath=self.intraopDataDir
    cmd = ('cp -a '+imagePath+'. '+intraopPath)
    os.system(cmd)


  def changeOpacity(self,node):

    # current slider value
    opacity=float(self.opacitySlider.value)

    # set opactiy
    layoutManager=slicer.app.layoutManager()
    redWidget = layoutManager.sliceWidget('Red')
    compositNode = redWidget.mrmlSliceCompositeNode()
    compositNode.SetForegroundOpacity((opacity/100))

  def loadAndSetdata(self):

    #load data
    slicer.util.loadLabelVolume('/Users/peterbehringer/MyImageData/A_PREOP_DIR/Case1-t2ax-TG-rater1.nrrd')
    preoplabelVolumeNode=slicer.mrmlScene.GetNodesByName('Case1-t2ax-TG-rater1').GetItemAsObject(0)

    slicer.util.loadVolume('/Users/peterbehringer/MyImageData/A_PREOP_DIR/Case1-t2ax-N4.nrrd')
    preopImageVolumeNode=slicer.mrmlScene.GetNodesByName('Case1-t2ax-N4').GetItemAsObject(0)

    slicer.util.loadLabelVolume('/Users/peterbehringer/MyImageData/ProstateRegistrationValidation/Segmentations/Rater1/Case1-t2ax-intraop-TG-rater1.nrrd')
    intraopLabelVolume=slicer.mrmlScene.GetNodesByName('Case1-t2ax-intraop-TG-rater1').GetItemAsObject(0)

    slicer.util.loadVolume('/Users/peterbehringer/MyImageData/ProstateRegistrationValidation/Images/Case1-t2ax-intraop.nrrd')
    intraopImageVolume=slicer.mrmlScene.GetNodesByName('Case1-t2ax-intraop').GetItemAsObject(0)

    slicer.util.loadMarkupsFiducialList('/Users/peterbehringer/MyImageData/A_PREOP_DIR/Case1-landmarks.fcsv')
    preopTargets=slicer.mrmlScene.GetNodesByName('Case1-landmarks').GetItemAsObject(0)

    # set nodes in Selector
    self.preopVolumeSelector.setCurrentNode(preopImageVolumeNode)
    self.preopLabelSelector.setCurrentNode(preoplabelVolumeNode)
    self.intraopVolumeSelector.setCurrentNode(intraopImageVolume)
    # self.intraopLabelSelector.setCurrentNode(intraopLabelVolume)
    self.fiducialSelector.setCurrentNode(preopTargets)

  def loadPreopData(self):

    # this function finds all volumes and fiducials in a directory and loads them into slicer

    fidList=[]
    volumeList=[]
    labelList=[]

    for nrrd in os.listdir(self.settings.value('RegistrationModule/preopLocation')):
      if len(nrrd)-nrrd.rfind('.nrrd') == 5:
        volumeList.append(self.settings.value('RegistrationModule/preopLocation')+'/'+nrrd)

    print ('volumes found :')
    print volumeList

    for fcsv in os.listdir(self.settings.value('RegistrationModule/preopLocation')):
      if len(fcsv)-fcsv.rfind('.fcsv') == 5:
        fidList.append(self.settings.value('RegistrationModule/preopLocation')+'/'+fcsv)


    print ('fiducials found :')
    print fidList

    # TODO: distinguish between image data volumes and labelmaps

    # load testdata and create Nodes
    preoplabelVolume=slicer.util.loadLabelVolume('/Users/peterbehringer/MyImageData/A_PREOP_DIR/t2ax-label.nrrd')
    preoplabelVolumeNode=slicer.mrmlScene.GetNodesByName('t2ax-label').GetItemAsObject(0)

    preopImageVolume=slicer.util.loadVolume('/Users/peterbehringer/MyImageData/A_PREOP_DIR/t2ax-N4.nrrd')
    preopImageVolumeNode=slicer.mrmlScene.GetNodesByName('t2ax-N4').GetItemAsObject(0)

    preopTargets=slicer.util.loadMarkupsFiducialList('/Users/peterbehringer/MyImageData/A_PREOP_DIR/Targets.fcsv')
    preopTargetsNode=slicer.mrmlScene.GetNodesByName('Targets').GetItemAsObject(0)


    # use label contours
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed").SetUseLabelOutline(True)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow").SetUseLabelOutline(True)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen").SetUseLabelOutline(True)

    # set Layout to redSliceViewOnly
    lm=slicer.app.layoutManager()
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

    # set orientation to axial

    layoutManager=slicer.app.layoutManager()
    redWidget = layoutManager.sliceWidget('Red')
    redLogic=redWidget.sliceLogic()
    sliceNodeRed=redLogic.GetSliceNode()
    sliceNodeRed.SetOrientationToAxial()

    # set markups visible

    self.markupsLogic=slicer.modules.markups.logic()
    self.markupsLogic.SetAllMarkupsVisibility(preopTargetsNode,1)

    # set markups for registration
    self.fiducialSelector.setCurrentNode(preopTargetsNode)


    # rotate volume to plane
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed").RotateToVolumePlane(preoplabelVolumeNode)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow").RotateToVolumePlane(preoplabelVolumeNode)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen").RotateToVolumePlane(preoplabelVolumeNode)

    # jump to first markup slice
    slicer.modules.markups.logic().JumpSlicesToNthPointInMarkup(preopTargetsNode.GetID(),1)

    # Fit Volume To Screen
    slicer.app.applicationLogic().FitSliceToAll()

    # Set Fiducial Properties
    markupsDisplayNode=preopTargetsNode.GetDisplayNode()

    # Set Textscale
    markupsDisplayNode.SetTextScale(1.9)

    # Set Glyph Size
    markupsDisplayNode.SetGlyphScale(1.0)

  def testFunction(self):

     print 'TestFUNCTION ENTERED'

   # self.createLoadableFileListFromSelection()

  def getSelectedSeriesFromSelector(self):

    # this function returns a List of names of the series
    # that are selected in Intraop Series Selector

    checkedItems = [x for x in self.seriesItems if x.checkState()]
    self.selectedSeries=[]

    for x in checkedItems:
      self.selectedSeries.append(x.text())

    return self.selectedSeries

  def createLoadableFileListFromSelection(self):

    # create dcmFileList that lists all .dcm files in directory
    dcmFileList = []
    self.selectedFileList=[]
    db=slicer.dicomDatabase

    for dcm in os.listdir(self.intraopDataDir):
      print ('current file = ' +str(dcm))
      if len(dcm)-dcm.rfind('.dcm') == 4 and dcm != ".DS_Store":
        dcmFileList.append(self.intraopDataDir+'/'+dcm)
      if dcm != ".DS_Store":
        print (' files doesnt have DICOM ending')
        dcmFileList.append(self.intraopDataDir+'/'+dcm)

    print ('dcmFileList is ready')
    print dcmFileList

    # get the selected Series List
    self.selectedSeriesList=self.getSelectedSeriesFromSelector()


    # write all selected files in selectedFileList
    for file in dcmFileList:
     print ('current file L1101 : '+str(file))
     if db.fileValue(file,'0008,103E') in self.selectedSeriesList:
       self.selectedFileList.append(file)

    print self.selectedFileList
    # create a list with lists of files of each series in them
    self.loadableList=[]

    # add all found series to loadableList
    for series in self.selectedSeriesList:
      fileListOfSeries =[]
      for file in self.selectedFileList:
        if db.fileValue(file,'0008,103E') == series:
          fileListOfSeries.append(file)
      self.loadableList.append(fileListOfSeries)

    print ('loadableList :')
    print self.loadableList




  def loadSeriesIntoSlicer(self):

    self.createLoadableFileListFromSelection()

    # create DICOMScalarVolumePlugin and load selectedSeries data from files into slicer
    scalarVolumePlugin = slicer.modules.dicomPlugins['DICOMScalarVolumePlugin']()

    # check if selectedPatient == importPatient

    try:
      loadables = scalarVolumePlugin.examine(self.loadableList)

    except:
      print ('There is nothing to load. You have to select series')

    """
    # load series into slicer
    for s in range(len(loadables)):
      print str(len(loadables))
      print ('loadables name : '+str(loadables[s].name))
      name = loadables[s].name
      v=scalarVolumePlugin.load(loadables[s])
      v.SetName(name)
      slicer.mrmlScene.AddNode(v)
    """

    name = loadables[0].name
    v=scalarVolumePlugin.load(loadables[0])
    v.SetName(name)
    slicer.mrmlScene.AddNode(v)

    # set last inputVolume Node as Reference Volume in Label Selection
    self.referenceVolumeSelector.setCurrentNode(v)

    # set last inputVolume Node as Intraop Image Volume in Registration
    self.intraopVolumeSelector.setCurrentNode(v)

    # Fit Volume To Screen
    slicer.app.applicationLogic().FitSliceToAll()

    # Allow PatientSelector to be updated
    self.updatePatientSelectorFlag = True

    self.enterLabelSelectionSection()

  def cleanup(self):
    pass

  def waitingForSeriesToBeCompleted(self):

    self.updatePatientSelectorFlag = False

    print ('***** New Data in intraop directory detected ***** ')
    print ('waiting 2 more seconds for Series to be completed')

    qt.QTimer.singleShot(5000,self.importDICOMseries)

  def importDICOMseries(self):

    newFileList= []
    self.seriesList= []
    indexer = ctk.ctkDICOMIndexer()
    db=slicer.dicomDatabase

    # create a List NewFileList that contains only new files in the intraop directory
    for item in os.listdir(self.intraopDataDir):
      if item not in self.currentFileList:
        newFileList.append(item)

    print ('Step 1: newFileList: ')
    print newFileList
    print ()

    # import file in DICOM database
    for file in newFileList:
     if not file == ".DS_Store":
       indexer.addFile(db,str(self.intraopDataDir+'/'+file),None)
       print ('file '+str(file)+' was added by Indexer')

       # add Series to seriesList
       if db.fileValue(str(self.intraopDataDir+'/'+file),'0008,103E') not in self.seriesList:
         importfile=str(self.intraopDataDir+'/'+file)
         self.seriesList.append(db.fileValue(importfile,'0008,103E'))

    indexer.addDirectory(db,str(self.intraopDataDir))
    indexer.waitForImportFinished()

    print ('Step 2: seriesList: ')
    print self.seriesList
    print ''

    # create Checkable Item in GUI

    self.seriesModel.clear()
    self.seriesItems = []

    for s in range(len(self.seriesList)):
      seriesText = self.seriesList[s]
      self.currentSeries=seriesText
      sItem = qt.QStandardItem(seriesText)
      self.seriesItems.append(sItem)
      self.seriesModel.appendRow(sItem)
      sItem.setCheckable(1)
      if "PROSTATE" in seriesText:
        sItem.setCheckState(1)


    print('')
    print('DICOM import finished')
    print('Those series are indexed into slicer.dicomDatabase')
    print self.seriesList

    # check, if selectedPatient == incomePatient
    # set warning Flag = False if not

    for file in newFileList:
      if file != ".DS_Store" and db.fileValue(self.intraopDataDir+'/'+file,'0010,0020') != self.currentID:
        self.warningFlag=True
      else:
        self.warningFlag=False


    if self.warningFlag:
      self.patientNotMatching(self.currentID,db.fileValue(str(self.intraopDataDir+'/'+newFileList[2]),'0010,0020'))

    if not self.tabWidget.currentIndex == 0:
      print ('here comes the change function')
      self.tabBar.setTabIcon(0,self.newImageDataIcon)





  def patientNotMatching(self,selectedPatient,incomePatient):

    # create Pop-Up Window
    self.notifyUserWindow = qt.QDialog(slicer.util.mainWindow())
    self.notifyUserWindow.setWindowTitle("Patients Not Matching")
    self.notifyUserWindow.setLayout(qt.QVBoxLayout())

    # create Text Label
    self.textLabel = qt.QLabel()
    self.notifyUserWindow.layout().addWidget(self.textLabel)
    self.textLabel.setText('WARNING: You selected Patient ID '+selectedPatient+', but Patient ID '+incomePatient+' just arrived in the income folder. ')

    # create Push Button
    self.pushButton = qt.QPushButton("OK")
    self.notifyUserWindow.layout().addWidget(self.pushButton)
    self.pushButton.connect('clicked(bool)',self.hideWindow)

    # show the window
    self.notifyUserWindow.show()

  def hideWindow(self):
    self.notifyUserWindow.hide()

  def createCurrentFileList(self):

    self.currentFileList=[]
    for item in os.listdir(self.intraopDataDir):
      self.currentFileList.append(item)

  def initializeListener(self):

    numberOfFiles = len([item for item in os.listdir(self.intraopDataDir)])
    self.temp=numberOfFiles
    self.setlastNumberOfFiles(numberOfFiles)
    self.createCurrentFileList()
    self.startTimer()

  def startTimer(self):
    numberOfFiles = len([item for item in os.listdir(self.intraopDataDir)])

    if self.getlastNumberOfFiles() < numberOfFiles:
     self.waitingForSeriesToBeCompleted()

     self.setlastNumberOfFiles(numberOfFiles)
     qt.QTimer.singleShot(500,self.startTimer)

    else:
     self.setlastNumberOfFiles(numberOfFiles)
     qt.QTimer.singleShot(500,self.startTimer)

  def setlastNumberOfFiles(self,number):
    self.temp = number

  def getlastNumberOfFiles(self):
    return self.temp

  def notifyUser(self,seriesName):
    # create Pop-Up Window
    self.notifyUserWindow = qt.QDialog(slicer.util.mainWindow())
    self.notifyUserWindow.setWindowTitle("New Series")
    self.notifyUserWindow.setLayout(qt.QVBoxLayout())

    # create Text Label
    self.textLabel = qt.QLabel()
    self.notifyUserWindow.layout().addWidget(self.textLabel)
    self.textLabel.setText("New Series are ready to be imported")

    # create Push Button
    self.pushButton = qt.QPushButton("Import new series"+"  "+seriesName)
    self.notifyUserWindow.layout().addWidget(self.pushButton)
    self.pushButton.connect('clicked(bool)',self.loadSeriesIntoSlicer)


    # create Push Button
    self.pushButton2 = qt.QPushButton("Not Now")
    self.notifyUserWindow.layout().addWidget(self.pushButton2)
    self.notifyUserWindow.show()

  def onStartSegmentationButton(self):

    self.setQuickSegmentationModeON()
    logic = RegistrationModuleLogic()
    logic.run()


  def setQuickSegmentationModeON(self):
    self.startLabelSegmentationButton.setEnabled(0)
    self.startQuickSegmentationButton.setEnabled(0)
    self.applySegmentationButton.setEnabled(1)

  def setQuickSegmentationModeOFF(self):
    self.startLabelSegmentationButton.setEnabled(1)
    self.startQuickSegmentationButton.setEnabled(1)
    self.applySegmentationButton.setEnabled(0)



  def onApplySegmentationButton(self):

    # create logic
    logic = RegistrationModuleLogic()

    # set parameter for modelToLabelmap CLI Module
    inputVolume=self.referenceVolumeSelector.currentNode()

    # get InputModel
    clipModelNode=slicer.mrmlScene.GetNodesByName('clipModelNode')
    clippingModel=clipModelNode.GetItemAsObject(0)

    # run CLI-Module
    outputLabelmap = logic.modelToLabelmap(inputVolume,clippingModel)

    # set Labelmap for Registration
    self.intraopLabelSelector.setCurrentNode(outputLabelmap)

    # re-set Buttons
    self.setQuickSegmentationModeOFF()
    # take draw tool with label 0 for correction

    import EditorLib
    editUtil = EditorLib.EditUtil.EditUtil()

    lm = slicer.app.layoutManager()

    drawEffect=EditorLib.DrawEffectOptions()
    drawEffect.setMRMLDefaults()
    drawEffect.__del__()

    # select drawTool in red Slice Widget
    sliceWidget = lm.sliceWidget('Red')
    drawTool=EditorLib.DrawEffectTool(sliceWidget)

    # set Value of labelmap
    editUtil.setLabel(0)


  def onStartLabelSegmentationButton(self):

    # disable QuickSegmentationButton
    self.startQuickSegmentationButton.setEnabled(0)

    #TODO: Create LabelMap

    intraopLabelMap=slicer.vtkMRMLScalarVolumeNode()
    intraopLabelMap.SetLabelMap(1)
    intraopLabelMap.SetName('intraop-label')
    slicer.mrmlScene.AddNode(intraopLabelMap)

    # TODO : Set Master Volume and Labelmap

    print ('after entering')

    # choose Draw-Tool

    import EditorLib
    editUtil = EditorLib.EditUtil.EditUtil()

    lm = slicer.app.layoutManager()

    drawEffect=EditorLib.DrawEffectOptions()
    drawEffect.setMRMLDefaults()
    drawEffect.__del__()

    # select drawTool in red Slice Widget
    sliceWidget = lm.sliceWidget('Red')

    #TODO change Icon
    drawTool=EditorLib.DrawEffectTool(sliceWidget)

    # set Value of labelmap
    editUtil.setLabel(1)

    # enable QuickSegmentationButton
    self.startQuickSegmentationButton.setEnabled(1)

  def applyRegistration(self):

    fixedVolume= self.intraopVolumeSelector.currentNode()
    movingVolume = self.preopVolumeSelector.currentNode()
    fixedLabel=self.intraopLabelSelector.currentNode()
    movingLabel=self.preopLabelSelector.currentNode()

    if fixedVolume and movingVolume and fixedLabel and movingLabel:

     # check, if import is correct
     if fixedVolume == None or movingVolume == None or fixedLabel == None or movingLabel == None:
       print 'Please see input parameters'


     ##### OUTPUT TRANSFORMS

     # define output linear Rigid transform
     outputTransformRigid=slicer.vtkMRMLLinearTransformNode()
     outputTransformRigid.SetName('transform-Rigid')

     # define output linear Affine transform
     outputTransformAffine=slicer.vtkMRMLLinearTransformNode()
     outputTransformAffine.SetName('transform-Affine')

     # define output BSpline transform
     outputTransformBSpline=slicer.vtkMRMLBSplineTransformNode()
     outputTransformBSpline.SetName('transform-BSpline')

     ##### OUTPUT VOLUMES

     # define output volume Rigid
     outputVolumeRigid=slicer.vtkMRMLScalarVolumeNode()
     outputVolumeRigid.SetName('reg-Rigid')

     # define output volume Affine
     outputVolumeAffine=slicer.vtkMRMLScalarVolumeNode()
     outputVolumeAffine.SetName('reg-Affine')

     # define output volume BSpline
     outputVolumeBSpline=slicer.vtkMRMLScalarVolumeNode()
     outputVolumeBSpline.SetName('reg-BSpline')

     # add output nodes
     slicer.mrmlScene.AddNode(outputVolumeRigid)
     slicer.mrmlScene.AddNode(outputVolumeBSpline)
     slicer.mrmlScene.AddNode(outputVolumeAffine)
     slicer.mrmlScene.AddNode(outputTransformRigid)
     slicer.mrmlScene.AddNode(outputTransformAffine)
     slicer.mrmlScene.AddNode(outputTransformBSpline)


     #   ++++++++++      RIGID REGISTRATION       ++++++++++

     paramsRigid = {'fixedVolume': fixedVolume,
                    'movingVolume': movingVolume,
                    'fixedBinaryVolume' : fixedLabel,
                    'movingBinaryVolume' : movingLabel,
                    'outputTransform' : outputTransformRigid.GetID(),
                    'outputVolume' : outputVolumeRigid.GetID(),
                    'maskProcessingMode' : "ROI",
                    'initializeTransformMode' : "useCenterOfROIAlign",
                    'useRigid' : True,
                    'useAffine' : False,
                    'useScaleVersor3D' : False,
                    'useScaleSkewVersor3D' : False,
                    'useROIBSpline' : False,
                    'useBSpline' : False,}

     # run Rigid Registration
     self.cliNode=None
     self.cliNode=slicer.cli.run(slicer.modules.brainsfit, self.cliNode, paramsRigid, wait_for_completion = True)


     #   ++++++++++      AFFINE REGISTRATION       ++++++++++

     paramsAffine = {'fixedVolume': fixedVolume,
               'movingVolume': movingVolume,
               'fixedBinaryVolume' : fixedLabel,
               'movingBinaryVolume' : movingLabel,
               'outputTransform' : outputTransformAffine.GetID(),
               'outputVolume' : outputVolumeAffine.GetID(),
               'maskProcessingMode' : "ROI",
               'initializeTransformMode' : "useCenterOfROIAlign",
               'useAffine' : True}

     # run Affine Registration
     self.cliNode=None
     self.cliNode=slicer.cli.run(slicer.modules.brainsfit, self.cliNode, paramsAffine, wait_for_completion = True)

     #   ++++++++++      BSPLINE REGISTRATION       ++++++++++

     paramsBSpline = {'fixedVolume': fixedVolume,
                      'movingVolume': movingVolume,
                      'outputVolume' : outputVolumeBSpline.GetID(),
                      'bsplineTransform' : outputTransformBSpline.GetID(),
                      'movingBinaryVolume' : movingLabel,
                      'fixedBinaryVolume' : fixedLabel,
                      # 'linearTransform' : outputTransformLinear.GetID(),
                      'initializeTransformMode' : "useCenterOfROIAlign",
                      'samplingPercentage' : "0.002",
                      'useRigid' : True,
                      'useAffine' : True,
                      'useROIBSpline' : True,
                      'useBSpline' : True,
                      'useScaleVersor3D' : True,
                      'useScaleSkewVersor3D' : True,
                      'splineGridSize' : "3,3,3",
                      'numberOfIterations' : "1500",
                      'maskProcessing' : "ROI",
                      'outputVolumePixelType' : "float",
                      'backgroundFillValue' : "0",
                      'maskInferiorCutOffFromCenter' : "1000",
                      'interpolationMode' : "Linear",
                      'minimumStepLength' : "0.005",
                      'translationScale' : "1000",
                      'reproportionScale' : "1",
                      'skewScale' : "1",
                      'numberOfHistogramBins' : "50",
                      'numberOfMatchPoints': "10",
                      'numberOfSamples' : "100000",
                      'fixedVolumeTimeIndex' : "0",
                      'movingVolumeTimeIndex' : "0",
                      'medianFilterSize' : "0,0,0",
                      'ROIAutoDilateSize' : "0",
                      'relaxationFactor' : "0.5",
                      'maximumStepLength' : "0.2",
                      'failureExitCode' : "-1",
                      'numberOfThreads': "-1",
                      'debugLevel': "0",
                      'costFunctionConvergenceFactor' : "1.00E+09",
                      'projectedGradientTolerance' : "1.00E-05",
                      'maxBSplineDisplacement' : "0",
                      'maximumNumberOfEvaluations' : "900",
                      'maximumNumberOfCorrections': "25",
                      'metricSamplingStrategy' : "Random",
                      'costMetric' : "MMI",
                      'removeIntensityOutliers' : "0",
                      'ROIAutoClosingSize' : "9",
                      'maskProcessingMode' : "ROI"}


     # run BSpline Registration
     self.cliNode=None
     self.cliNode=slicer.cli.run(slicer.modules.brainsfit, self.cliNode, paramsBSpline, wait_for_completion = True)


     #   ++++++++++      TRANSFORM FIDUCIALS        ++++++++++


     if self.fiducialSelector.currentNode() != None:

       print ("Perform Target Transform")

       # TODO: Clone Fiducials 3 times more
       # create fiducials for every transform and harden them?

       # get transform
       transformNode=slicer.mrmlScene.GetNodesByName('transform-BSpline').GetItemAsObject(0)

       print ('TRANSFORM NODE: ')
       print transformNode
       print ''
       print ''

       # get fiducials
       fiducialNode=slicer.mrmlScene.GetNodesByName('Targets').GetItemAsObject(0)
       fiducialNode2=slicer.mrmlScene.GetNodesByName('Targets').GetItemAsObject(0)

       #debug_start:
       if fiducialNode == None:
         fiducialNode=slicer.mrmlScene.GetNodesByName('Case1-landmarks').GetItemAsObject(0)
       #debug_end

       # apply transform
       fiducialNode.SetAndObserveTransformNodeID(transformNode.GetID())
       fiducialNode.SetName('targets-REG')

       # harden the transform
       tfmLogic = slicer.modules.transforms.logic()
       tfmLogic.hardenTransform(fiducialNode)

       # rename the targets to "[targetname]-REG"
       numberOfTargets=fiducialNode.GetNumberOfFiducials()
       print ('number of targets : '+str(numberOfTargets))

       for index in range(numberOfTargets):
         oldname=fiducialNode.GetNthFiducialLabel(index)
         fiducialNode.SetNthFiducialLabel(index,str(oldname)+'-REG')
         print ('changed name from '+oldname+' to '+str(oldname)+'-REG')


    # switch to Evaluation Section
    self.tabWidget.setCurrentIndex(3)

    # Get SliceWidgets
    layoutManager=slicer.app.layoutManager()

    redWidget = layoutManager.sliceWidget('Red')
    yellowWidget = layoutManager.sliceWidget('Yellow')

    compositNodeRed = redWidget.mrmlSliceCompositeNode()
    compositNodeYellow = yellowWidget.mrmlSliceCompositeNode()

    # set Side By Side View to compare volumes
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)

    # Hide Labels
    compositNodeRed.SetLabelOpacity(0)
    compositNodeYellow.SetLabelOpacity(0)

    # Set Intraop Image Foreground in Red
    compositNodeRed.SetBackgroundVolumeID(fixedVolume.GetID())

    # Set REG Image Background in Red
    compositNodeRed.SetForegroundVolumeID(outputVolumeBSpline.GetID())

    # set markups visible
    self.markupsLogic=slicer.modules.markups.logic()
    self.markupsLogic.SetAllMarkupsVisibility(fiducialNode,1)

    # set Intraop Image Foreground in Yellow
    compositNodeYellow.SetBackgroundVolumeID(fixedVolume.GetID())

    # jump slice to show Targets in Yellow
    slicer.modules.markups.logic().JumpSlicesToNthPointInMarkup(fiducialNode.GetID(),1)

    # set both orientations to axial
    redLogic=redWidget.sliceLogic()
    yellowLogic=yellowWidget.sliceLogic()

    sliceNodeRed=redLogic.GetSliceNode()
    sliceNodeYellow=yellowLogic.GetSliceNode()

    sliceNodeRed.SetOrientationToAxial()
    sliceNodeYellow.SetOrientationToAxial()

    # make REG markups visible in yellow slice view
    dispNode = fiducialNode.GetDisplayNode()
    yellowSliceNode=slicer.mrmlScene.GetNodesByName('Yellow').GetItemAsObject(0)
    dispNode.AddViewNodeID(yellowSliceNode.GetID())

    # show preop markups in red slicer view

    dispNode2=fiducialNode2.GetDisplayNode()
    redSliceNode=slicer.mrmlScene.GetNodesByName('Red').GetItemAsObject(0)
    dispNode2.AddViewNodeID(redSliceNode.GetID())



#
# RegistrationModuleLogic
#



class RegistrationModuleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    self.delayDisplay(description)

    if self.enableScreenshots == 0:
      return

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

  def run(self):
    """
    Run the actual algorithm
    """

    # set four up view, select persistent fiducial marker as crosshair
    self.setVolumeClipUserMode()

    # let user place Fiducials
    self.placeFiducials()

  def setVolumeClipUserMode(self):

    # TODO: Hide all other label

    # set Layout to redSliceViewOnly
    lm=slicer.app.layoutManager()
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

    # fit Slice View to FOV
    red=lm.sliceWidget('Red')
    redLogic=red.sliceLogic()
    redLogic.FitSliceToAll()

    # set the mouse mode into Markups fiducial placement
    placeModePersistence = 1
    slicer.modules.markups.logic().StartPlaceMode(placeModePersistence)

  def updateModel(self,observer,caller):

    clipModelNode=slicer.mrmlScene.GetNodesByName('clipModelNode')
    self.clippingModel=clipModelNode.GetItemAsObject(0)

    inputMarkupNode=slicer.mrmlScene.GetNodesByName('inputMarkupNode')
    inputMarkup=inputMarkupNode.GetItemAsObject(0)

    import VolumeClipWithModel
    clipLogic=VolumeClipWithModel.VolumeClipWithModelLogic()
    clipLogic.updateModelFromMarkup(inputMarkup, self.clippingModel)

  def placeFiducials(self):

    # Create empty model node
    self.clippingModel = slicer.vtkMRMLModelNode()
    self.clippingModel.SetName('clipModelNode')
    slicer.mrmlScene.AddNode(self.clippingModel)

    # Create markup display fiducials - why do i need that?
    displayNode = slicer.vtkMRMLMarkupsDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)

    # create markup fiducial node
    inputMarkup = slicer.vtkMRMLMarkupsFiducialNode()
    inputMarkup.SetName('inputMarkupNode')
    slicer.mrmlScene.AddNode(inputMarkup)
    inputMarkup.SetAndObserveDisplayNodeID(displayNode.GetID())

    # set Text Scale to 0
    inputMarkupDisplayNode=slicer.mrmlScene.GetNodesByName('inputMarkupNode').GetItemAsObject(0).GetDisplayNode()

    # Set Textscale
    inputMarkupDisplayNode.SetTextScale(0)

    # Set Glyph Size
    inputMarkupDisplayNode.SetGlyphScale(2.0)

    # add Observer
    inputMarkup.AddObserver(vtk.vtkCommand.ModifiedEvent,self.updateModel)

  def modelToLabelmap(self,inputVolume,clippingModel):

    """
    PARAMETER FOR MODELTOLABELMAP CLI MODULE:
    Parameter (0/0): sampleDistance
    Parameter (0/1): labelValue
    Parameter (1/0): InputVolume
    Parameter (1/1): surface
    Parameter (1/2): OutputVolume
    """

    # initialize Label Map
    outputLabelMap=slicer.vtkMRMLScalarVolumeNode()
    outputLabelMap.SetLabelMap(1)
    outputLabelMap.SetName('Intraop Label Map')
    slicer.mrmlScene.AddNode(outputLabelMap)

    # TODO: check if parameters == None

    # define params
    params = {'sampleDistance': 0.2, 'labelValue': 5, 'InputVolume' : inputVolume.GetID(), 'surface' : clippingModel.GetID(), 'OutputVolume' : outputLabelMap.GetID()}

    # run ModelToLabelMap-CLI Module
    cliNode=slicer.cli.run(slicer.modules.modeltolabelmap, None, params, wait_for_completion=True)

    # use label contours
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed").SetUseLabelOutline(True)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow").SetUseLabelOutline(True)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen").SetUseLabelOutline(True)

    # rotate volume to plane
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed").RotateToVolumePlane(outputLabelMap)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeYellow").RotateToVolumePlane(outputLabelMap)
    slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeGreen").RotateToVolumePlane(outputLabelMap)

    # set Layout to redSliceViewOnly
    lm=slicer.app.layoutManager()
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)

    # fit Slice View to FOV
    red=lm.sliceWidget('Red')
    redLogic=red.sliceLogic()
    redLogic.FitSliceToAll()

    # set Label Opacity Back
    redWidget = lm.sliceWidget('Red')
    compositNodeRed = redWidget.mrmlSliceCompositeNode()
    compositNodeRed.SetLabelOpacity(1)

    # remove markup fiducial node
    slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetNodesByName('clipModelNode').GetItemAsObject(0))

    # remove model node
    slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetNodesByName('inputMarkupNode').GetItemAsObject(0))

    return outputLabelMap


  def runBRAINSFit(self,movingImage,fixedImage,movingImageLabel,fixedImageLabel):

    # rigidly register followup to baseline
    # TODO: do this in a separate step and allow manual adjustment?
    # TODO: add progress reporting (BRAINSfit does not report progress though)
    pNode = self.parameterNode()
    baselineVolumeID = pNode.GetParameter('baselineVolumeID')
    followupVolumeID = pNode.GetParameter('followupVolumeID')
    self.__followupTransform = slicer.vtkMRMLLinearTransformNode()
    slicer.mrmlScene.AddNode(self.__followupTransform)

    parameters = {}
    parameters["fixedVolume"] = baselineVolumeID
    parameters["movingVolume"] = followupVolumeID
    parameters["initializeTransformMode"] = "useMomentsAlign"
    parameters["useRigid"] = True
    parameters["useScaleVersor3D"] = True
    parameters["useScaleSkewVersor3D"] = True
    parameters["useAffine"] = True
    parameters["linearTransform"] = self.__followupTransform.GetID()

    self.__cliNode = None
    self.__cliNode = slicer.cli.run(slicer.modules.brainsfit, self.__cliNode, parameters)

    self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
    self.__registrationStatus.setText('Wait ...')
    self.__registrationButton.setEnabled(0)

    """def processRegistrationCompletion(self, node, event):
    status = node.GetStatusString()
    self.__registrationStatus.setText('Registration '+status)
    if status == 'Completed':
      self.__registrationButton.setEnabled(1)

      pNode = self.parameterNode()
      followupNode = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
      followupNode.SetAndObserveTransformNodeID(self.__followupTransform.GetID())

      Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

      pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())"""

class RegistrationModuleTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)


  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_RegistrationModule1()

  def test_RegistrationModule1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """
    print (' ___ performing selfTest ___ ')