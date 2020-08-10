from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import time
import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PPSTM_simple import newPPSTM_simple
import PPSTM.pyPPSTM.basUtils as Bu
import PPSTM.pyPPSTM.elements as elements




class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, figure, parentApp=None, parentWidget=None, width=20, height=8, dpi=100):
        self.fig = figure
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.parent = parentApp
        self.setParent(parentWidget)
        FigureCanvasQTAgg.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        # Following are the variables from inputs. Kind of like private
        # Putting all the self variables to a dictionary
        self.myDict = {'dft_code': 'fireball',
                       'sample_orbs': 'sp',
                       'spin': None,
                       'pbc': (0, 0),
                       'data_format': '.npy',
                       'kValue': 0.24,
                       'qValue': 0.00,
                       'x': [0.00, 20.00, 0.1],     # [xmin, xmax, dx]
                       'y': [0.00, 20.00, 0.1],     # [ymin, ymax, dy]
                       'z': [10.00, 10.00, 0.1],    # [zmin, zmax, dz]
                       'scan_type': 'V-scan',
                       'etaValue': 0.1,
                       'wf_decay': 0.5,
                       'V': -0.5,
                       'Vmax': 2.0,
                       'dV': 0.1,
                       'tipOrbS': 1.0,
                       'tipOrbPxy': 0.0,
                       'OMP_NUM_THREADS': 1}   
        self.map = 'dIdV'
        self.Vindx = 0
        self.Hindx = 0
        self.paths = ['./PPSTM/', 'crazy_mol', '']

        # App settings
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Application Window")

        # 'Dummy' widget to hold the whole layout
        self.mainWidget = QWidget(self)

        # Main layout. Horizontal box. Graphics on the left, functionality on the right.
        mainLayout = QHBoxLayout(self)
        self.plotData = newPPSTM_simple(self.myDict, self.paths)
        self.myCanvas = MplCanvas(figure=self.plotImage(self.plotData[4], self.plotData[3], self.plotData[5],self.plotData[7],self.plotData[6], self.Hindx, self.Vindx, self.map), parentApp=self, parentWidget=self.mainWidget, width=20, height=8, dpi=150,)
        mainLayout.addWidget(self.myCanvas)

        # Control Part on the right. Vertical Box Layout.
        controlLayout = QVBoxLayout(self)
        mainLayout.addLayout(controlLayout)
####################################  INPUT PART  ##############################################

        # Input part 1 - HBox. First top region of the control part. 
        inputLayout1 = QHBoxLayout(self)
        controlLayout.addLayout(inputLayout1)

        # Adding codes to layout
        codesBox = QVBoxLayout(self); inputLayout1.addLayout(codesBox)
        codesBox.addWidget(QLabel("codes"))

        # codes scroll bar
        codes = QComboBox(self); codesBox.addWidget(codes)
        codes.addItems(['fireball', 'gpaw', 'aims', 'cp2k'])
        codes.setCurrentIndex(codes.findText(self.myDict['dft_code']))
        codes.currentIndexChanged[str].connect(self.selectCode)
        

        # Adding orbitals to layout
        orbitalBox = QVBoxLayout(self); inputLayout1.addLayout(orbitalBox)
        orbitalBox.addWidget(QLabel("sample orbital"))

        # oribital scroll bar
        orbitals = QComboBox(self); orbitalBox.addWidget(orbitals)
        orbitals.addItems(['sp', 'spd'])
        orbitals.setCurrentIndex(orbitals.findText(self.myDict['sample_orbs']))
        orbitals.currentIndexChanged[str].connect(self.selectOrbital)

        # Adding spin to Layout
        spinBox = QVBoxLayout(self); inputLayout1.addLayout(spinBox)
        spinBox.addWidget(QLabel("spin"))

        # Spin scroll bar
        spin = QComboBox(self); spinBox.addWidget(spin)
        spin.addItems(['None', 'both', 'alpha', 'beta'])
        spin.setCurrentIndex(spin.findText(str(self.myDict['spin'])))
        spin.currentIndexChanged[str].connect(self.selectSpin)

        # Adding pbc to layout
        pbcBox = QVBoxLayout(self); inputLayout1.addLayout(pbcBox)
        pbcBox.addWidget(QLabel("pbc"))

        # pbc scroll bar
        pbc = QComboBox(); pbcBox.addWidget(pbc)
        pbc.addItems(['00', '11', '22'])
        pbc.currentIndexChanged[str].connect(self.selectPbc)

        # Input part 2 - HBox. Second top region of the control part.
        inputLayout2 = QHBoxLayout(self)
        controlLayout.addLayout(inputLayout2)

        # Adding path text box to the layout
        pathBox = QVBoxLayout(self); inputLayout2.addLayout(pathBox)
        pathBox.addWidget(QLabel("Input files path"))
        # Creating input files path text box 
        # In this case self is needed in order to reference later to the written text inside.
        self.path_inputFiles = QLineEdit(self); pathBox.addWidget(self.path_inputFiles)

        # Adding geometry_path text box to the layout
        geometryBox = QVBoxLayout(self); inputLayout2.addLayout(geometryBox)
        geometryBox.addWidget(QLabel("Geometry file path"))
        # Creating geometry file path text box
        self.geometryPath = QLineEdit(self); geometryBox.addWidget(self.geometryPath)

        # Adding CP2K/GPAW name text box to the layout
        nameBox = QVBoxLayout(self); inputLayout2.addLayout(nameBox)
        nameBox.addWidget(QLabel("CP2K/GPAW name"))
        # Creating name text box
        self.name = QLineEdit(self); nameBox.addWidget(self.name)

        # Button importing packages and everything
        importButton = QPushButton("Import", self); inputLayout2.addWidget(importButton)
        importButton.clicked.connect(self.imported)

################################# END OF INPUT PART #######################################

        line = QFrame(self); controlLayout.addWidget(line); line.setFrameShape(QFrame.HLine); line.setFrameShadow(QFrame.Sunken)

############################## GRID AND RUNNING OPTIONS ####################################


########## grl1 - grid running layout 1. First row of grid running settings

        grl1 = QHBoxLayout(self); controlLayout.addLayout(grl1); 

        # Adding format to layout
        grl1.addWidget(QLabel("         Format"))
        # Creating format scroll bar
        self.formatBar = QComboBox(self); grl1.addWidget(self.formatBar);
        self.formatBar.addItems(['.xsf', '.npy'])
        self.formatBar.setCurrentIndex(self.formatBar.findText(self.myDict['data_format']))
        self.formatBar.currentIndexChanged[str].connect(self.selectFormat)
        
        # Adding K number range
        grl1.addWidget(QLabel('             K: '))
        self.k = QDoubleSpinBox(self); grl1.addWidget(self.k);
        self.k.setRange(0.0, 2.0); self.k.setValue(self.myDict['kValue']); self.k.setSingleStep(0.05)
        self.k.valueChanged.connect(self.selectK)

        # Adding Q number range
        grl1.addWidget(QLabel('             Q: '))
        self.q = QDoubleSpinBox(self); grl1.addWidget(self.q);
        self.q.setRange(0.0, 2.0); self.q.setValue(self.myDict['qValue']); self.q.setSingleStep(0.05)
        self.q.valueChanged.connect(self.selectQ)
        
############# grl2 - grid running layout 2. Second row of grid running settings

        grl2 = QHBoxLayout(self); controlLayout.addLayout(grl2);

        # Adding Xmin number range
        grl2.addWidget(QLabel('         Xmin: '))
        self.xMin = QDoubleSpinBox(self); grl2.addWidget(self.xMin);
        self.xMin.setRange(0.0, 20.0); self.xMin.setValue(self.myDict['x'][0]); self.xMin.setSingleStep(0.05)
        self.xMin.valueChanged.connect(self.selectX)

        # Adding Xmax number range
        grl2.addWidget(QLabel('         Xmax: '))
        self.xMax = QDoubleSpinBox(self); grl2.addWidget(self.xMax);
        self.xMax.setRange(0.0, 20.0); self.xMax.setValue(self.myDict['x'][1]); self.xMax.setSingleStep(0.05)
        self.xMax.valueChanged.connect(self.selectX)

        # Adding dX number range
        grl2.addWidget(QLabel('             dX: '))
        self.dx = QDoubleSpinBox(self); grl2.addWidget(self.dx);
        self.dx.setRange(0.0, 20.0); self.dx.setValue(self.myDict['x'][2]); self.dx.setSingleStep(0.05)
        self.dx.valueChanged.connect(self.selectX)

############# grl3 - grid running layout 3. Third row of grid running settings

        grl3 = QHBoxLayout(self); controlLayout.addLayout(grl3);

        # Adding Ymin number range
        grl3.addWidget(QLabel('         Ymin: '))
        self.yMin = QDoubleSpinBox(self); grl3.addWidget(self.yMin);
        self.yMin.setRange(0.0, 20.0); self.yMin.setValue(self.myDict['y'][0]); self.yMin.setSingleStep(0.05)
        self.yMin.valueChanged.connect(self.selectY)

        # Adding Ymax number range
        grl3.addWidget(QLabel('         Ymax: '))
        self.yMax = QDoubleSpinBox(self); grl3.addWidget(self.yMax);
        self.yMax.setRange(0.0, 20.0); self.yMax.setValue(self.myDict['y'][1]); self.yMax.setSingleStep(0.05)
        self.yMax.valueChanged.connect(self.selectY)

        # Adding dY number range
        grl3.addWidget(QLabel('             dY: '))
        self.dy = QDoubleSpinBox(self); grl3.addWidget(self.dy);
        self.dy.setRange(0.0, 20.0); self.dy.setValue(self.myDict['y'][2]); self.dy.setSingleStep(0.05)
        self.dy.valueChanged.connect(self.selectY)

############# grl4 - grid running layout 4. Fourth row of grid running settings

        grl4 = QHBoxLayout(self); controlLayout.addLayout(grl4);

        # Adding Zmin number range
        grl4.addWidget(QLabel('         Zmin: '))
        self.zMin = QDoubleSpinBox(self); grl4.addWidget(self.zMin);
        self.zMin.setRange(0.0, 20.0); self.zMin.setValue(self.myDict['z'][0]); self.zMin.setSingleStep(0.05)
        self.zMin.valueChanged.connect(self.selectZ)

        # Adding Zmax number range
        grl4.addWidget(QLabel('         Zmax: '))
        self.zMax = QDoubleSpinBox(self); grl4.addWidget(self.zMax);
        self.zMax.setRange(0.0, 20.0); self.zMax.setValue(self.myDict['z'][1]); self.zMax.setSingleStep(0.05)
        self.zMax.valueChanged.connect(self.selectZ)

        # Adding dZ number range
        grl4.addWidget(QLabel('             dZ: '))
        self.dz = QDoubleSpinBox(self); grl4.addWidget(self.dz);
        self.dz.setRange(0.0, 20.0); self.dz.setValue(self.myDict['z'][2]); self.dz.setSingleStep(0.05)
        self.dz.valueChanged.connect(self.selectZ)

########## grl5 - grid running layout 5. Fifth row of grid running settings

        grl5 = QHBoxLayout(self); controlLayout.addLayout(grl5); 

        # Adding scan type to layout
        grl5.addWidget(QLabel("         Scan type"))
        # Creating scan type scroll bar
        scan = QComboBox(self); grl5.addWidget(scan);
        scan.addItems(['dIdV', 'V-scan', 'states'])
        scan.setCurrentIndex(scan.findText(self.myDict['scan_type']))
        scan.currentIndexChanged[str].connect(self.selectScanType)
        
        # Adding Eta number range
        grl5.addWidget(QLabel('             Eta: '))
        self.eta = QDoubleSpinBox(self); grl5.addWidget(self.eta);
        self.eta.setRange(0.0, 2.0); self.eta.setValue(self.myDict['etaValue']); self.eta.setSingleStep(0.05)
        self.eta.valueChanged.connect(self.selectEta)

        # Adding WF_decay number range (wfd)
        grl5.addWidget(QLabel('             WF_decay: '))
        self.wfd = QDoubleSpinBox(self); grl5.addWidget(self.wfd);
        self.wfd.setRange(0.0, 2.0); self.wfd.setValue(self.myDict['wf_decay']); self.wfd.setSingleStep(0.05)
        self.wfd.valueChanged.connect(self.selectWF_decay)


############# grl6 - grid running layout 6. Sixth row of grid running settings

        grl6 = QHBoxLayout(self); controlLayout.addLayout(grl6);

        # Adding V(min) number range
        grl6.addWidget(QLabel('         V(min): '))
        self.vMin = QDoubleSpinBox(self); grl6.addWidget(self.vMin);
        self.vMin.setRange(-2.0, 2.0); self.vMin.setValue(self.myDict['V']); self.vMin.setSingleStep(0.05)
        self.vMin.valueChanged.connect(self.selectV)

        # Adding Vmax number range
        grl6.addWidget(QLabel('         Vmax: '))
        self.vMax = QDoubleSpinBox(self); grl6.addWidget(self.vMax);
        self.vMax.setRange(0.0, 20.0); self.vMax.setValue(self.myDict['Vmax']); self.vMax.setSingleStep(0.05)
        self.vMax.valueChanged.connect(self.selectV)

        # Adding dV number range
        grl6.addWidget(QLabel('             dV: '))
        self.dv = QDoubleSpinBox(self); grl6.addWidget(self.dv);
        self.dv.setRange(0.0, 20.0); self.dv.setValue(self.myDict['dV']); self.dv.setSingleStep(0.05)
        self.dv.valueChanged.connect(self.selectV)

############# grl8 - grid running layout 8. Eith row of grid running settings

        grl8 = QHBoxLayout(self); controlLayout.addLayout(grl8);

        # Adding Tip orb s number range
        grl8.addWidget(QLabel('         Tip orb. s: '))
        self.orbS = QDoubleSpinBox(self); grl8.addWidget(self.orbS);
        self.orbS.setRange(-2.0, 2.0); self.orbS.setValue(self.myDict['tipOrbS']); self.orbS.setSingleStep(0.05)
        self.orbS.valueChanged.connect(self.selectTipOrbS)

        # Adding Vmax number range
        grl8.addWidget(QLabel('         Tip orb. pxy: '))
        self.orbPxy = QDoubleSpinBox(self); grl8.addWidget(self.orbPxy);
        self.orbPxy.setRange(0.0, 20.0); self.orbPxy.setValue(self.myDict['tipOrbPxy']); self.orbPxy.setSingleStep(0.05)
        self.orbPxy.valueChanged.connect(self.selectTipOrbPxy)

        # Adding dV number range
        grl8.addWidget(QLabel('             OMP_NUM_THREADS: '))
        self.ont = QDoubleSpinBox(self); grl8.addWidget(self.ont);
        self.ont.setRange(0.0, 20.0); self.ont.setValue(self.myDict['OMP_NUM_THREADS']); self.ont.setSingleStep(0.05)
        self.ont.valueChanged.connect(self.selectONT)

############# grl7 - grid running layout 7. Seventh row of grid running settings

        grl7 = QHBoxLayout(self); controlLayout.addLayout(grl7);

        # Buttons
        importGrid = QPushButton("Import Grid", self); grl7.addWidget(importGrid)
        importGrid.clicked.connect(self.importGridClicked)

        createGrid = QPushButton("Create Grid", self); grl7.addWidget(createGrid)
        createGrid.clicked.connect(self.createGridClicked)

        run = QPushButton("Run", self); grl7.addWidget(run)
        run.clicked.connect(self.running)


######################### END OF GRID AND RUNNING OPTIONS #######################################

        line = QFrame(self); controlLayout.addWidget(line); line.setFrameShape(QFrame.HLine); line.setFrameShadow(QFrame.Sunken)

############################# VISUALIZING OPTIONS PART ####################################

####### vo1 - visualizing options part 1, row 1
        vo1 = QHBoxLayout(self); controlLayout.addLayout(vo1)

        # Map type scroll bar
        vo1.addWidget(QLabel(       "Map type"))
        mapType = QComboBox(self); vo1.addWidget(mapType)
        mapType.addItems(['dIdV', 'STM'])
        mapType.currentIndexChanged[str].connect(self.selectMapType)

        # Adding Voltage Index number range
        vo1.addWidget(QLabel('             Voltage Index: '))
        self.vIndx = QSpinBox(self); vo1.addWidget(self.vIndx);
        self.vIndx.setRange(0, 10000); self.vIndx.setValue(self.Vindx); self.vIndx.setSingleStep(0.05)
        self.vIndx.valueChanged.connect(self.selectVindx)

        # Adding Height Index number range
        vo1.addWidget(QLabel('             Height Index: '))
        self.hIndx = QSpinBox(self); vo1.addWidget(self.hIndx);
        self.hIndx.setRange(0, 10000); self.hIndx.setValue(self.Hindx); self.hIndx.setSingleStep(0.05)
        self.hIndx.valueChanged.connect(self.selectHindx)

####### vo2 - visualizing options part 2, row 2

        vo2 = QHBoxLayout(self); controlLayout.addLayout(vo2)

        # Buttons
        saveImg = QPushButton("Save image", self); vo2.addWidget(saveImg)
        saveImg.clicked.connect(self.saveImage)

        saveData = QPushButton("Save data", self); vo2.addWidget(saveData)
        saveData.clicked.connect(self.saveData)

        saveOptions = QPushButton("Save options", self); vo2.addWidget(saveOptions)
        saveOptions.clicked.connect(self.saveOptions)

############################# VISUALIZING OPTIONS END ####################################

        # Adding layout to the main widget 
        self.mainWidget.setLayout(mainLayout)
        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)


    # TODO 
    # set it in a way that each function changes the self values form the top.
    # To set correct position of the labels you can just add spacings to the labels inside the string.
    # string inputs such as scan type, lowercase them before passing to findText in widgets.


    def selectCode(self, code):
        self.myDict['dft_code'] = code

    def selectOrbital(self, orbital):
        self.myDict['sample_orbs'] = orbital

    def selectSpin(self, spin):
        self.myDict['spin'] = spin 

    def selectPbc(self, pbc):
        self.myDict['pbc'] = (pbc[0], pbc[1])
    
    def imported(self):
        # check if path to input files is given, if not give error and do not let to run
        inputPath = self.path_inputFiles.text()
        geometry_path = self.geometryPath.text() 
        cp2kName = self.name.text()
        if len(inputPath) == 0 or len(cp2kName) == 0:
            print ('Input path not given')
        else:
            self.paths = [inputPath, cp2kName, geometry_path]

    def selectFormat(self, myFormat):
        self.myDict['data_format'] = myFormat

    def selectK(self):
        self.myDict['kValue'] = self.k.value()
    
    def selectQ(self):
        self.myDict['qValue'] = self.q.value()

    def selectX(self):
        self.myDict['x'][0] = self.xMin.value()
        self.myDict['x'][1] = self.xMax.value()
        self.myDict['x'][2] = self.dx.value()
    
    def selectY(self):
        self.myDict['y'][0] = self.yMin.value()
        self.myDict['y'][1] = self.yMax.value()
        self.myDict['y'][2] = self.dy.value()

    def selectZ(self):
        self.myDict['z'][0] = self.zMin.value()
        self.myDict['z'][1] = self.zMax.value()
        self.myDict['z'][2] = self.dz.value()

    def selectScanType(self, scanType):
        self.myDict['scan_type'] = scanType
    
    def selectEta(self):
        self.myDict['etaValue'] = self.eta.value()

    def selectWF_decay(self):
        self.myDict['wf_decay'] = self.wfd.value()

    def selectV(self):
        self.myDict['V'] = self.vMin.value()
        self.myDict['Vmax'] = self.vMax.value()
        self.myDict['dV'] = self.dv.value()
    
    def selectTipOrbS(self):
        self.myDict['tipOrbS'] = self.orbS.value()
    
    def selectTipOrbPxy(self):
        self.myDict['tipOrbPxy'] = self.orbPxy.value()
    
    def selectONT(self):
        self.myDict['OMP_NUM_THREADS'] = self.ont.value()
    
    def importGridClicked(self):
        print("import grid clicked")
    
    def createGridClicked(self):
        print("create grid clicked")
    
    def running(self):
        plotData = newPPSTM_simple(self.myDict, self.paths)
        self.myCanvas = MplCanvas(figure=self.plotImage(plotData[4], plotData[3], plotData[5],plotData[7],plotData[6], self.Hindx, self.Vindx, self.map), parentApp=self, parentWidget=self.mainWidget, width=20, height=8, dpi=150,)
        
    def selectMapType(self, chosenMap):
        self.map = chosenMap
    
    def selectVindx(self):
        self.Vindx = self.vIndx.value()
    
    def selectHindx(self):
        self.Hindx = self.hIndx.value()

    def saveImage(self):
        self.saveImageClicked = True
    
    def saveData(self):
        print ("Data saved")
    
    def saveOptions(self):
        print ("Options saved")
        
    
    def plotAtoms( self, atoms, myfigure, atomSize=0.1, edge=True, ec='k', color='w' ):
        es = atoms[0]; xs = atoms[1]; ys = atoms[2]
        for i in range(len(xs)):
            fc = '#%02x%02x%02x' % elements.ELEMENT_DICT[es[i]][7] #; print "DEBUG: fc", fc ; ##fc = '#FFFFFF' ##
            if not edge:
                ec=fc
            circle=plt.Circle( ( xs[i], ys[i] ), atomSize, fc=fc, ec=ec  )
            myfigure.add_artist(circle)
    
    def plotGeom( self, myfigure, atoms=None, atomSize=0.1 ):
        if atoms is not None:
            self.plotAtoms( atoms, myfigure, atomSize=atomSize )
    
    def plotImage(self, geom_plot, didv, current, extent, lvec, height, voltage, mapType):

        print("We go to plotting ")
        # print "DEBUG: long name:::", namez[vv],';height:%03d;tip:'  %k,tip_type,';',tip_orb
        #name_plot=namez[voltage]+';height:'+str(height)+';tip:'+tip_type+';'+tip_orb
        plt.close()
        if mapType == 'dIdV':
        # ploting part here:
            myFigure = plt.figure( figsize=(0.5 * lvec[1,0] , 0.5 * lvec[2,1] ) )
            plt.imshow(didv[voltage,height,:,:], origin='image', extent=extent , cmap='gray')
            self.plotGeom(myFigure, atoms=geom_plot)
            plt.xlabel(r' Tip_x $\AA$')
            plt.ylabel(r' Tip_y $\AA$')
            #plt.title("dIdV:"+name_plot)
        elif mapType == 'STM':
        # ploting part here:
            myFigure = plt.figure( figsize=(0.5 * lvec[1,0] , 0.5 * lvec[2,1] ) )
            plt.imshow(current[voltage,height,:,:], origin='image', extent=extent , cmap='gray')
            self.plotGeom(myFigure, atoms=geom_plot)
            plt.xlabel(r' Tip_x $\AA$')
            plt.ylabel(r' Tip_y $\AA$')
            #plt.title("STM:"+name_plot)
        return myFigure

                

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())