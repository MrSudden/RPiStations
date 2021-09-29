import sys, math, requests, itertools
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtGui  import *
from PyQt5.QtCore import *

class SignalHelper(QObject):
    """
    Defines the signal available from a running worker thread.
    Signal supported: (result: str, str, str, str)
    """
    result = pyqtSignal(str, str, str, str)

class Worker(QRunnable):
    """
    ProcessWorker thread.
    Inherits from QRunnable to handle thread setup, siganl and wrap-up.
    """

    def __init__(self, code):
        super().__init__()
        self.signal = SignalHelper()
        self.code = str(code)

    @pyqtSlot()
    def run(self) -> None:
        """
        Executes the fetch operation from server and delivers to the GUI class
        """
        resp = requests.get(url="http://dcraz8317.pythonanywhere.com/station")
        holder = resp.json()["data"]

        for tm in holder[self.code]:
            item1 = tm["id"]
            item2 = tm["status"]
            eta = str(self.formatSeconds(math.floor(tm["eta"] / 60))) + str(":")
            eta += self.formatSeconds(tm["eta"] % 60)
            item3 = self.getTimes(tm["eta"])
            item4 = eta
            print(item1, item2, item3, item4, sep="\t")
            self.signal.result.emit(item1, item2, item3, item4)
        
        self.setAutoDelete(True)

    def getTimes(self, val):
        ti = datetime.now()
        si = ti + timedelta(seconds=val)
        return str(self.formatSeconds(si.hour)) + str(":") + str(self.formatSeconds(si.minute)) + str(":") + str(self.formatSeconds(si.second))    

    def formatSeconds(self, val):
        tmp = ""
        if val < 10:
            tmp = str("0" + str(val))
        else:
            tmp = str(val)
        return tmp

class ListModel(QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super(ListModel, self).__init__(*args, **kwargs)
        self.datas = todos or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.datas[index.row()]
            return text

    def rowCount(self, index):
        return len(self.datas)

    def clear(self, todos=None):
        self.datas = todos or []

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class App(QWidget):
    def __init__(self, wid, hei):
        super().__init__()
        self.title = 'Bosso'
        self.code = 'bosso'
        self.left = 0
        self.top = 0
        self.width = wid
        self.height = hei
        self.threadpool = QThreadPool()
        self.initUI()

        self.clock = QTimer()
        self.clock.setInterval(500)
        self.clock.timeout.connect(self.refreshClock)

        self.timer = QTimer()
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.updateViews)
        self.timer.start()
        self.clock.start()

    def refreshClock(self):
            # Update time label
            self.timeLabel.setText(str(datetime.now().strftime("%a, %d %b %Y %H:%M:%S") + str(" GMT")))

    def updateViews(self):
        self.model1.clear()
        self.model2.clear()
        self.model3.clear()
        self.model4.clear()
        # Trigger refresh.
        self.model1.layoutChanged.emit()
        self.model2.layoutChanged.emit()
        self.model3.layoutChanged.emit()
        self.model4.layoutChanged.emit()

        self.worker = Worker(self.code)
        self.worker.signal.result.connect(self.add)
        self.threadpool.tryStart(self.worker)

    def add(self, _1, _2, _3, _4):
        """
        Add an item to our model list.
        """
        item1 = _1
        item2 = _2
        item3 = _3
        item4 = _4

        if item1 and item2 and item3 and item4: # Don't add empty strings.
            # Access the list via the model.
            self.model1.datas.append(item1)
            self.model2.datas.append(item2)
            self.model3.datas.append(item3)
            self.model4.datas.append(item4)
            # Trigger refresh.
            self.model1.layoutChanged.emit()
            self.model2.layoutChanged.emit()
            self.model3.layoutChanged.emit()
            self.model4.layoutChanged.emit()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.pal = self.palette()
        self.pal.setColor(QPalette.Background, Qt.black)
        self.setPalette(self.pal)

        self.hlay = QHBoxLayout()
        self.hlay1 = QHBoxLayout()
        self.hlay11 = QHBoxLayout()
        self.hlay2 = QHBoxLayout()
        self.hlay3 = QHBoxLayout()
        self.hlay4 = QHBoxLayout()
        self.stat = QLabel("Station:  " + self.title)
        self.stat.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular}")
        self.timeLabel = QLabel(str(datetime.now().strftime("%a, %d %b %Y %H:%M:%S") + str(" GMT")))
        self.timeLabel.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular }")
        self.busLabel = QLabel("  Bus ID")
        self.busLabel.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.busLabel.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular }")
        self.statusLabel = QLabel("  Status")
        self.statusLabel.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.statusLabel.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular }")
        self.etaLabel = QLabel("  ETA")
        self.etaLabel.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.etaLabel.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular }")
        self.tomeLabel = QLabel("  Countdown")
        self.tomeLabel.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.tomeLabel.setStyleSheet("QLabel { color: white; font-family: Open Sans Regular }")
        self.line = QHLine()
        self.line.setMaximumHeight(3)
        self.line.setMaximumWidth(int(self.width - int(self.width * 0.034)))
        self.line1 = QHLine()
        self.line1.setMaximumHeight(3)
        self.line1.setMaximumWidth(int(self.width - int(self.width * 0.034)))

        self.hlay.addSpacing(int(self.width * 0.017))
        self.hlay.addWidget(self.stat)
        self.hlay.addStretch()
        self.hlay.addWidget(self.timeLabel)
        self.hlay.addSpacing(int(self.width * 0.017))

        self.hlay1.addSpacing(int(self.width * 0.017))
        self.hlay1.addWidget(self.line)
        self.hlay1.addSpacing(int(self.width * 0.017))
        self.hlay11.addSpacing(int(self.width * 0.017))
        self.hlay11.addWidget(self.line1)
        self.hlay11.addSpacing(int(self.width * 0.017))

        self.createList()

        self.hlay2.addSpacing(int(self.width * 0.017))
        self.hlay2.addWidget(self.busLabel)
        self.hlay2.addWidget(self.statusLabel)
        self.hlay2.addWidget(self.etaLabel)
        self.hlay2.addWidget(self.tomeLabel)
        self.hlay2.addSpacing(int(self.width * 0.017))

        self.hlay3.addSpacing(int(self.width * 0.017))
        self.hlay3.addWidget(self.list1)
        self.hlay3.addWidget(self.list2)
        self.hlay3.addWidget(self.list3)
        self.hlay3.addWidget(self.list4)
        self.hlay3.addSpacing(int(self.width * 0.017))

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addSpacing(int(self.height * 0.024))
        self.layout.addLayout(self.hlay)
        self.layout.addSpacing(int(self.height * 0.024))
        self.layout.addLayout(self.hlay1)
        self.layout.addSpacing(int(self.height * 0.024))
        self.layout.addLayout(self.hlay2)
        self.layout.addSpacing(int(self.height * 0.012))
        self.layout.addLayout(self.hlay11)
        self.layout.addSpacing(int(self.height * 0.012))
        self.layout.addLayout(self.hlay3)
        self.layout.addSpacing(int(self.height * 0.012))
        self.setLayout(self.layout) 

        # Show widget
        self.show()

    def createList(self):
        self.list1 = QListView()
        self.list2 = QListView()
        self.list3 = QListView()
        self.list4 = QListView()

        self.model1 = ListModel()
        self.model2 = ListModel()
        self.model3 = ListModel()
        self.model4 = ListModel()

        # busids = ["RTC", "FTD"]
        # status = ["In Transit", "Delayed"]
        # etas = ["17:03", "17:03"]
        # tomes = ["08:38:43", "08:38:43"]

        # for t, y, u, i in itertools.zip_longest(busids, status, etas, tomes):
        #     item1 = t
        #     item2 = y
        #     item3 = u
        #     item4 = i
        #     self.add(item1, item2, item3, item4)

        self.list1.setModel(self.model1)
        self.list2.setModel(self.model2)
        self.list3.setModel(self.model3)
        self.list4.setModel(self.model4)

        self.list1.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.list2.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.list3.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))
        self.list4.setMaximumWidth(int(int(self.width - int(self.width * 0.034)) * 0.25))


        self.listPal1 = self.list1.palette()
        self.list1.setFont(QFont("Open Sans Regular", pointSize=int(self.height * 0.02)))
        self.list1.setSpacing(int(self.height * 0.01))
        self.listPal1.setColor(QPalette.Base, Qt.black)
        self.listPal1.setColor(QPalette.Text, Qt.white)
        self.list1.setPalette(self.listPal1)
        self.listPal2 = self.list2.palette()
        self.list2.setFont(QFont("Open Sans Regular", pointSize=int(self.height * 0.02)))
        self.list2.setSpacing(int(self.height * 0.01))
        self.listPal2.setColor(QPalette.Base, Qt.black)
        self.listPal2.setColor(QPalette.Text, Qt.white)
        self.list2.setPalette(self.listPal2)
        self.listPal3 = self.list3.palette()
        self.list3.setFont(QFont("Open Sans Regular", pointSize=int(self.height * 0.02)))
        self.list3.setSpacing(int(self.height * 0.01))
        self.listPal3.setColor(QPalette.Base, Qt.black)
        self.listPal3.setColor(QPalette.Text, Qt.white)
        self.list3.setPalette(self.listPal3)
        self.listPal4 = self.list4.palette()
        self.list4.setFont(QFont("Open Sans Regular", pointSize=int(self.height * 0.02)))
        self.list4.setSpacing(int(self.height * 0.01))
        self.listPal4.setColor(QPalette.Base, Qt.black)
        self.listPal4.setColor(QPalette.Text, Qt.white)
        self.list4.setPalette(self.listPal4)

        self.list1.setSelectionMode(QAbstractItemView.NoSelection)
        self.list2.setSelectionMode(QAbstractItemView.NoSelection)
        self.list3.setSelectionMode(QAbstractItemView.NoSelection)
        self.list4.setSelectionMode(QAbstractItemView.NoSelection)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    # print('Screen: %s' % screen.name())
    size = screen.size()
    # print('Size: %d x %d' % (size.width(), size.height()))
    rect = QDesktopWidget().screenGeometry(-1)
    print('Available: %d x %d' % (rect.width(), rect.height()))
    ex = App(rect.width(), rect.height())
    sys.exit(app.exec_())  