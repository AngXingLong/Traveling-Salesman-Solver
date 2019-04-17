import os, json
from SelectionAlgorithm import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import FormatStrFormatter
import traceback, sys

class CallHandler(QObject):
    @pyqtSlot()
    def onready(self):
        return
    def updateDistance(self,data):
        return

class QGoogleMap:
    def setCoordinates(self,coordinates):

        jsonString = []
        coordinates = copy.deepcopy(coordinates)

        while coordinates.isEmpty() == False:
            node = coordinates.dequeue()
            name = ""

            if node.name == node.userDefinedName:
                name = node.name
            else:
                name = "<b>{}</b><br>{}".format(node.userDefinedName,node.name)

            jsonString.append({"lat": node.lat, "lng": node.long, "content": "{}".format(name)})

        view.page().runJavaScript("setCoordinates("+ json.dumps(jsonString)+")")


    def updateCoordinates(self,coordinates):
        self.setCoordinates(coordinates)
        self.clearAll()
        self.setPolyLines()
        self.setMarkers()

    def clearAll(self):
        view.page().runJavaScript("clearMarkers();")
        view.page().runJavaScript("clearPolyLines();")

    def setPolyLines(self):
        view.page().runJavaScript("setPolyLines()")

    def setMarkers(self):
        view.page().runJavaScript("setMarkers()")

    def clearPreviousMarker(self):
        view.page().runJavaScript("clearPreviousMarker()")

    def clearMarkers(self):
        view.page().runJavaScript("clearMarkers();")

    def clearPolyLines(self):
        view.page().runJavaScript("clearPolyLines();")

    def calculateAndDisplayRoute(self):
        view.page().runJavaScript("calculateAndDisplayRoute();")



class PlotCanvas(FigureCanvas):

    numberOfPlots = 0

    def __init__(self, xlabel,ylabel,title):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        plt.style.use('seaborn')

        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def clearPlot(self):
        self.fig.clf()

    def plot(self, yAxis, xAxis, Label):

        ax = self.figure.add_subplot(111)
        ax.plot(yAxis,xAxis, label = Label,alpha=0.75)
        ax.set(xlabel=self.xlabel, ylabel=self.ylabel, title=self.title)
        #ax.set(xlabel='Number Of Nodes', ylabel='Time(s)', title='Time Complexity')
        ax.legend()
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        self.draw()

class GUI(QMainWindow):

    maxNodeSize = 26
    onGoingProcess = False


    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):

        self.mapWindow()
        self.compareView()
        self.widgetController = QStackedWidget(self)
        self.setCentralWidget(self.widgetController)

        switchToMapView = QAction("&Map", self)
        switchToMapView.triggered.connect(self.setAsMapWidget)

        switchToCompareView = QAction("&Compare", self)
        switchToCompareView.triggered.connect(self.setAsCompareWidget)

        self.toolbar = self.addToolBar('Commands')
        self.toolbar.addAction(switchToMapView)
        self.toolbar.addAction(switchToCompareView)

        self.selectionAlgorithm = SelectionAlgorithm()

        self.widgetController.addWidget(self.mapWidget)
        # self.widgetController.addWidget(self.compareViewWidget)

        self.setGeometry(300, 300, 1280,720)
        self.setWindowTitle('Traveling Salesman Solver')

        self.show()


    def compareView(self):

        self.algroTable = QTableWidget()

        self.algroTable.setRowCount(10)
        self.algroTable.setColumnCount(6)
        self.algroTable.setHorizontalHeaderLabels(["Algorithm","Number Of\nNodes","Time\nTaken(s)","Total\nDistance(km)","Number Of \nIteration","Percentage\nDifference"])
        #,"Algroithm","Best Case","Avg Case","Worst Case"
        header = self.algroTable.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(5, QHeaderView.Stretch)


        bigOTable = QTableWidget()

        bigOTable.setRowCount(10)
        bigOTable.setColumnCount(4)
        bigOTable.setHorizontalHeaderLabels(["Algorithm","Worst Case", "Avg Case", "Best Case"])

        header = bigOTable.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        bigOTable.setItem(0, 0, QTableWidgetItem("Nearest Neighbour"))
        bigOTable.setItem(0, 1, QTableWidgetItem("O(n)"))
        bigOTable.setItem(0, 2, QTableWidgetItem("O(n)"))
        bigOTable.setItem(0, 3, QTableWidgetItem("O(n)"))

        bigOTable.setItem(1, 0, QTableWidgetItem("Brute Force"))
        bigOTable.setItem(1, 1, QTableWidgetItem("O(n!)"))
        bigOTable.setItem(1, 2, QTableWidgetItem("O(n!)"))
        bigOTable.setItem(1, 3, QTableWidgetItem("O(n!)"))

        bigOTable.setItem(2, 0, QTableWidgetItem("Branch And Bound"))
        bigOTable.setItem(2, 1, QTableWidgetItem("O(n!)"))
        bigOTable.setItem(2, 2, QTableWidgetItem("O(n)"))
        bigOTable.setItem(2, 3, QTableWidgetItem("O(1)"))

        bigOTable.setItem(3, 0, QTableWidgetItem("Two Opt"))
        bigOTable.setItem(3, 1, QTableWidgetItem("O(n^2)"))
        bigOTable.setItem(3, 2, QTableWidgetItem("O(n^2)"))
        bigOTable.setItem(3, 3, QTableWidgetItem("O(n^2)"))


        rightPanel = QVBoxLayout()
        rightPanel.setAlignment(Qt.AlignCenter)

        self.testNodeInput = QLineEdit()
        self.testNodeInput.setValidator(QIntValidator())

        button = QPushButton('Start Comparison', self)
        button.clicked.connect(self.startComparison)
        info = QLabel("The traveling salesman problem includes a starting and ending point", self)
        info.setWordWrap(True)
        rightPanel.addWidget(info)
        self.errorLabelCompareView = QLabel("")
        self.errorLabelCompareView.setStyleSheet('color: red')
        rightPanel.addWidget(self.errorLabelCompareView)
        rightPanel.addWidget(QLabel("Number Of Nodes"))
        rightPanel.addWidget(self.testNodeInput)
        rightPanel.addWidget(button)

        compareViewLayout = QHBoxLayout()
        compareViewLayout.setSpacing(10)
        self.chart = PlotCanvas('Number Of Nodes','Time(s)','Time Complexity')
        self.performanceChart = PlotCanvas('Number Of Nodes','Percentage Difference(%)','Performance Comparison With Base')
        tableChartLayout = QGridLayout()
        tableChartLayout.setRowStretch(0,2)
        tableChartLayout.setRowStretch(1,1)
        #tableChartLayout.setColumnStretch(0, 1)
       # tableChartLayout.setColumnStretch(1, 1)

        tableChartLayout.addWidget(self.chart,0,0)
        tableChartLayout.addWidget(self.performanceChart, 0,1)
        tableChartLayout.addWidget(self.algroTable,1,0)
        tableChartLayout.addWidget(self.algroTable,1,0)
        tableChartLayout.addWidget(bigOTable,1,1)

        compareViewLayout.addLayout(tableChartLayout,6)
        compareViewLayout.addLayout(rightPanel, 1)

        self.compareViewWidget = QWidget()
        self.compareViewWidget.setLayout(compareViewLayout)
    def calucatePercentageDiff(self,oldDist,newDist):
        diff = newDist - oldDist
        return round(diff/oldDist * 100,2)

    def startComparison(self):

        selectionAlgorithm = SelectionAlgorithm()

        if self.testNodeInput.text() == None or self.testNodeInput.text() == "":
            return

        numberOfNodes = int(self.testNodeInput.text())

        if 3 > numberOfNodes:
            self.errorLabelCompareView.setText("Min number of nodes to test is 3")
            return

        self.errorLabelCompareView.setText("")

        min = 3
        max = numberOfNodes + 1
        offset = max - min + 1

        algroTimeComplexData = {"Nearest Neighbour": [], "Brute Force": [], "Branch And Bound": [], "Two Opt": []}
        algroPerformaceData = {"Nearest Neighbour": [], "Brute Force": [], "Branch And Bound": [], "Two Opt": []}

        self.algroTable.setRowCount(0)
        self.algroTable.setRowCount(offset*(len(algroTimeComplexData)+1))

        count = 0

        self.algroTable.setItem(offset * count, 0, QTableWidgetItem("Base (No Algorithm)"))
        count += 1
        for i in algroTimeComplexData.keys():
            self.algroTable.setItem(offset*count, 0, QTableWidgetItem(i))
            count += 1


        row = 0
        nodes = []

        for i in range(min, max):
            selectionAlgorithm.setRandomNodes(i)
            selectionAlgorithm.setLastItemAsReturnNode()

            baseDistance = selectionAlgorithm.nodeList.convertToQueue()
            baseDistance.enqueue(copy.deepcopy(selectionAlgorithm.returnNode))
            baseDistance = round(selectionAlgorithm.getDistanceFromQueue(baseDistance),2)

            selectionAlgorithm.nearestNeighbour()
            count = 0

            self.algroTable.setItem(offset * count + row, 1,QTableWidgetItem(str(selectionAlgorithm.nodeSequence.size())))
            self.algroTable.setItem(offset * count + row, 2, QTableWidgetItem(str(0)))
            self.algroTable.setItem(offset * count + row, 3, QTableWidgetItem(str(baseDistance)))
            self.algroTable.setItem(offset * count + row, 4, QTableWidgetItem(str(1)))
            self.algroTable.setItem(offset * count + row, 5, QTableWidgetItem(str(0)))

            count += 1

            diff = self.calucatePercentageDiff(baseDistance, selectionAlgorithm.getTotalDistance())
            self.algroTable.setItem(offset*count + row, 1, QTableWidgetItem(str(selectionAlgorithm.nodeSequence.size())))
            self.algroTable.setItem(offset*count + row, 2, QTableWidgetItem(str(selectionAlgorithm.getTime())))
            self.algroTable.setItem(offset*count + row, 3, QTableWidgetItem(str(selectionAlgorithm.getTotalDistance())))
            self.algroTable.setItem(offset*count + row, 4, QTableWidgetItem(str(selectionAlgorithm.getIteration())))
            self.algroTable.setItem(offset * count + row, 5, QTableWidgetItem(str(diff)))

            algroTimeComplexData["Nearest Neighbour"].append(selectionAlgorithm.getTime())
            algroPerformaceData["Nearest Neighbour"].append(diff)

            selectionAlgorithm.bruteForce()
            count += 1
            diff = self.calucatePercentageDiff(baseDistance, selectionAlgorithm.getTotalDistance())
            self.algroTable.setItem(offset*count + row, 1, QTableWidgetItem(str(selectionAlgorithm.nodeSequence.size())))
            self.algroTable.setItem(offset*count + row, 2, QTableWidgetItem(str(selectionAlgorithm.getTime())))
            self.algroTable.setItem(offset*count + row, 3, QTableWidgetItem(str(selectionAlgorithm.getTotalDistance())))
            self.algroTable.setItem(offset*count + row, 4, QTableWidgetItem(str(selectionAlgorithm.getIteration())))
            self.algroTable.setItem(offset * count + row, 5, QTableWidgetItem(str(diff)))

            algroTimeComplexData["Brute Force"].append(selectionAlgorithm.getTime())
            algroPerformaceData["Brute Force"].append(diff)

            selectionAlgorithm.branchAndBound()
            count += 1
            diff = self.calucatePercentageDiff(baseDistance, selectionAlgorithm.getTotalDistance())
            self.algroTable.setItem(offset*count + row, 1, QTableWidgetItem(str(selectionAlgorithm.nodeSequence.size())))
            self.algroTable.setItem(offset*count + row, 2, QTableWidgetItem(str(selectionAlgorithm.getTime())))
            self.algroTable.setItem(offset*count + row, 3, QTableWidgetItem(str(selectionAlgorithm.getTotalDistance())))
            self.algroTable.setItem(offset*count + row, 4, QTableWidgetItem(str(selectionAlgorithm.getIteration())))
            self.algroTable.setItem(offset * count + row, 5, QTableWidgetItem(str(diff)))

            algroTimeComplexData["Branch And Bound"].append(selectionAlgorithm.getTime())
            algroPerformaceData["Branch And Bound"].append(diff)

            selectionAlgorithm.twoOpt()
            count += 1
            diff = self.calucatePercentageDiff(baseDistance, selectionAlgorithm.getTotalDistance())
            self.algroTable.setItem(offset*count + row, 1, QTableWidgetItem(str(selectionAlgorithm.nodeSequence.size())))
            self.algroTable.setItem(offset*count + row, 2, QTableWidgetItem(str(selectionAlgorithm.getTime())))
            self.algroTable.setItem(offset*count + row, 3, QTableWidgetItem(str(selectionAlgorithm.getTotalDistance())))
            self.algroTable.setItem(offset*count + row, 4, QTableWidgetItem(str(selectionAlgorithm.getIteration())))
            self.algroTable.setItem(offset * count + row, 5, QTableWidgetItem(str(diff)))

            algroTimeComplexData["Two Opt"].append(selectionAlgorithm.getTime())
            algroPerformaceData["Two Opt"].append(diff)

            nodes.append(i)
            row += 1

        self.chart.clearPlot()
        self.performanceChart.clearPlot()

        for k, v in algroTimeComplexData.items():
            self.chart.plot(nodes, v, k)

        for k, v in algroPerformaceData.items():
            self.performanceChart.plot(nodes, v, k)

        return


    def mapWindow(self):

        self.googleMapHandler = QGoogleMap()
        self.selectionAlgorithm = SelectionAlgorithm()

        rightPanel = QVBoxLayout()
        rightPanel.setSpacing(10)
        rightPanel.setAlignment(Qt.AlignTop)

        self.totalNodes = QLabel("0")
        self.timeLabel = QLabel("0s")
        self.distanceLabel = QLabel("0 Km")
        self.permutationLabel = QLabel("0")
        self.rightPanelWrapper(rightPanel, QLabel("Total Nodes:"), self.totalNodes, 1, 3)
        self.rightPanelWrapper(rightPanel, QLabel("Total Time:"), self.timeLabel, 1, 3)
        self.rightPanelWrapper(rightPanel, QLabel("Total Distance:"), self.distanceLabel, 1, 3)
        self.rightPanelWrapper(rightPanel, QLabel("Total Permutation:"), self.permutationLabel, 1, 3)

        self.previewComboBox = QComboBox(self)
        self.previewComboBox.addItem("Preview Speed: Default Normal")
        self.previewComboBox.addItem("Fast")
        self.previewComboBox.addItem("Normal")
        self.previewComboBox.addItem("Slow")
        self.previewComboBox.addItem("Disabled")
        rightPanel.addWidget(self.previewComboBox)
        self.previewComboBox.currentIndexChanged.connect(self.previewSpeedChange)

        self.algorithmComboBox = QComboBox(self)
        self.algorithmComboBox.addItem("Select Algorithm")
        self.algorithmComboBox.addItem("Nearest Neighbour")
        self.algorithmComboBox.addItem("Brute Force")
        self.algorithmComboBox.addItem("Branch And Bound")
        self.algorithmComboBox.addItem("Two Opt")

        rightPanel.addWidget(self.algorithmComboBox)

        self.randomNodeInput = QLineEdit()
        self.randomNodeInput.setValidator(QIntValidator())

        setRandomNodeButton = QPushButton('Set Rnd', self)
        setRandomNodeButton.clicked.connect(self.setRandomNodes)

        self.rightPanelWrapper(rightPanel, self.randomNodeInput, setRandomNodeButton, 4, 1)


        startSolvingButton = QPushButton('Start Solving', self)
        startSolvingButton.clicked.connect(self.processRoute)

        rightPanel.addWidget(startSolvingButton)

        self.errorLabel = QLabel("First item is treated as starting point\nLast item is treated as ending point")
        self.errorLabel.setStyleSheet('color: red')
        rightPanel.addWidget(self.errorLabel)

        self.ioTabLayout = QTabWidget()
        self.inputTab = QWidget()
        self.outputTab = QWidget()

        self.ioTabLayout.addTab(self.inputTab, "Input")
        self.ioTabLayout.addTab(self.outputTab, "Output")

        self.inputTab.layout = QVBoxLayout()
        self.outputTab.layout = QVBoxLayout()

        self.inputTable = QTableWidget()

        self.inputTable.setRowCount(self.maxNodeSize)
        self.inputTable.setColumnCount(1)
        self.inputTable.setHorizontalHeaderLabels(["Address/Name"])
        self.inputTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        """
        self.inputTable.setItem(0, 0, QTableWidgetItem("Singapore Polytechnic"))
        self.inputTable.setItem(1, 0, QTableWidgetItem("Ngee Ann Polytechnic"))
        self.inputTable.setItem(2, 0, QTableWidgetItem("Temasek Polytechnic"))
        self.inputTable.setItem(3,0, QTableWidgetItem("Nanyang Polytechnic"))
        self.inputTable.setItem(4,0, QTableWidgetItem("Republic Polytechnic"))
        """
        # self.tableWidget.doubleClicked.connect(self.on_click2)

        self.outputTable = QTableWidget()

        self.outputTable.setRowCount(self.maxNodeSize)
        self.outputTable.setColumnCount(2)
        self.outputTable.setHorizontalHeaderLabels(["Address/Name","Next Node\nDistance(km)"])
        self.outputTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        #self.outputTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.inputTab.layout.addWidget(self.inputTable)
        self.outputTab.layout.addWidget(self.outputTable)
        self.inputTab.setLayout(self.inputTab.layout)
        self.outputTab.setLayout(self.outputTab.layout)
        rightPanel.addWidget(self.ioTabLayout)

        self.mapWidget = QWidget()
        self.mapViewLayout = QHBoxLayout()
        self.mapViewLayout.setSpacing(10)
        self.mapViewLayout.addWidget(view, 4)
        self.mapViewLayout.addLayout(rightPanel, 1)

        self.mapWidget.setLayout(self.mapViewLayout)

    def setAsMapWidget(self):
        self.widgetController.removeWidget(self.compareViewWidget)
        self.widgetController.addWidget(self.mapWidget)

    def setAsCompareWidget(self):
        self.widgetController.removeWidget(self.mapWidget)
        self.widgetController.addWidget(self.compareViewWidget)

    def rightPanelWrapper(self,rightPanel,widget1,widget2,ratio1,ratio2):
        wrapper = QHBoxLayout()
        wrapper.addWidget(widget1, ratio1)
        wrapper.addWidget(widget2, ratio2)
        rightPanel.addLayout(wrapper)

    def setRandomNodes(self):
        if self.onGoingProcess:
            self.errorLabel.setText("Compution in progress please wait")
            return
        self.inputTable.setRowCount(0)
        self.inputTable.setRowCount(self.maxNodeSize)

        if self.randomNodeInput.text() == None or self.randomNodeInput.text() == "":
            return

        numberOfNodes = int(self.randomNodeInput.text())
        q = Queue()

        if numberOfNodes > 2 and self.maxNodeSize >= numberOfNodes:

            self.selectionAlgorithm = SelectionAlgorithm()
            self.selectionAlgorithm.setRandomNodes(numberOfNodes,True)

            for i in range(self.selectionAlgorithm.nodeList.size()):
                node = self.selectionAlgorithm.nodeList.search(i)
                self.inputTable.setItem(i, 0, QTableWidgetItem(node.name))
                q.enqueue(self.selectionAlgorithm.nodeList.search(i))

            self.selectionAlgorithm.setLastItemAsReturnNode()

        else:
            self.errorLabel.setText("Max number of nodes is {}\nMin number of nodes is 3".format(self.maxNodeSize))

        self.googleMapHandler.clearAll()
        self.googleMapHandler.setCoordinates(q)
        self.googleMapHandler.setMarkers()
        self.ioTabLayout.setCurrentIndex(0)

    def previewSpeedChange(self):
        self.selectionAlgorithm.setThreadSleepTime(self.previewComboBox.currentText())

    def completedRoute(self):

        self.googleMapHandler.clearPolyLines()
        self.googleMapHandler.clearMarkers()
        self.googleMapHandler.updateCoordinates(self.selectionAlgorithm.nodeSequence)
        self.updateRoute()
        self.onGoingProcess = False
        self.ioTabLayout.setCurrentIndex(1)

    def updateRoute(self):

        self.googleMapHandler.setCoordinates(self.selectionAlgorithm.nodeSequence)
        self.googleMapHandler.clearPolyLines()
        self.googleMapHandler.setPolyLines()

        self.totalNodes.setText("{}".format(self.selectionAlgorithm.getSize()))
        self.timeLabel.setText("{}s".format(self.selectionAlgorithm.getTime()))
        self.distanceLabel.setText("{} Km".format(self.selectionAlgorithm.getTotalDistance()))
        self.permutationLabel.setText("{}".format(self.selectionAlgorithm.getIteration()))

        tempQueue = copy.deepcopy(self.selectionAlgorithm.nodeSequence)

        self.outputTable.setRowCount(0)
        self.outputTable.setRowCount(self.maxNodeSize)

        for i in range(tempQueue.size()):
            node = tempQueue.dequeue()
            nextnode = tempQueue.peek()

            if node.name == node.userDefinedName:
                self.outputTable.setItem(i, 0, QTableWidgetItem(node.name))
            else:
                self.outputTable.setItem(i, 0, QTableWidgetItem("{} ({})".format(node.userDefinedName, node.name)))

            if nextnode is not None:
                self.outputTable.setItem(i, 1, QTableWidgetItem(
                    str(round(self.selectionAlgorithm.getDistanceBetweenNode(node, nextnode), 2))))


    def processRoute(self):
        if self.onGoingProcess:
            self.errorLabel.setText("Compution in progress please wait")
            return

        algoSelection = self.algorithmComboBox.currentText()

        if algoSelection == "Select Algorithm":
            self.errorLabel.setText("Please select an algorithm")
            return

        isEquals = True

        tableArray = []

        for i in range(self.inputTable.rowCount()):
            row =  self.inputTable.item(i, 0)
            if hasattr(row, 'text'):
                tableArray.append(row.text())

        if len(tableArray) ==  self.selectionAlgorithm.getSize():
            for i in range(self.selectionAlgorithm.nodeList.size() - 1):
                name =  self.selectionAlgorithm.nodeList.search(i).userDefinedName
                if tableArray[i] != name:
                    isEquals = False
                    break
            if self.selectionAlgorithm.returnNode.userDefinedName != tableArray[-1]:
                isEquals = False
        else:
            isEquals = False

        if not isEquals:
            self.selectionAlgorithm = SelectionAlgorithm()
            for i in range(self.inputTable.rowCount()):
                if hasattr(self.inputTable.item(i, 0), 'text'):
                    tabletext = self.inputTable.item(i, 0).text()
                    tabletext = tabletext.strip()
                    if tabletext:
                        if not self.selectionAlgorithm.setNode(self.inputTable.item(i, 0).text()):
                            self.errorLabel.setText("There is an error translating row {}".format(i + 1))
                            return

            self.selectionAlgorithm.setLastItemAsReturnNode()

            if 2 > self.selectionAlgorithm.getSize():
                self.errorLabel.setText("Number of nodes must be greater than 2")
                return


        self.selectionAlgorithm.setThreadSleepTime(self.previewComboBox.currentText())
        self.googleMapHandler.setCoordinates(self.selectionAlgorithm.getNodeListAsQueue())
        self.googleMapHandler.clearAll()
        self.googleMapHandler.setMarkers()

        if algoSelection == "Nearest Neighbour":
            worker = Worker(self.selectionAlgorithm.nearestNeighbour)
        elif algoSelection == "Brute Force":
            worker = Worker(self.selectionAlgorithm.bruteForce)
        elif algoSelection == "Branch And Bound":
            worker = Worker(self.selectionAlgorithm.branchAndBound)
        elif algoSelection == "Two Opt":
            worker = Worker(self.selectionAlgorithm.twoOpt)

        worker.signals.progress.connect(self.updateRoute)
        worker.signals.finished.connect(self.completedRoute)

        self.threadpool.start(worker)
        self.onGoingProcess = True
        self.ioTabLayout.setCurrentIndex(1)
        self.errorLabel.setText("")


class WorkerSignals(QObject):

    error = pyqtSignal(tuple)
    progress = pyqtSignal()
    finished = pyqtSignal()


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):

        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            #self.signals.result.emit(result)  # Return the result of the processing
            return
        finally:
            self.signals.finished.emit()  # Done


if __name__ == '__main__':
    app = QApplication(sys.argv)

    channel = QWebChannel()
    handler = CallHandler()
    view = QWebEngineView()
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "GoogleMap.html"))
    local_url = QUrl.fromLocalFile(file_path)
    channel.registerObject('handler', handler)
    view.page().setWebChannel(channel)
    view.load(local_url)

    ex = GUI()
    sys.exit(app.exec_())