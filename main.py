from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from downloadMusicUI import *
from fun import *
import threading
import os


class MyWindow(QMainWindow, Ui_MainWindow):
    # 自定义信号
    mySignal = pyqtSignal(str)
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        # dr=webdriver.Chrome(options=option,executable_path="chromedriver.exe")
        try:
            self.dr=webdriver.Chrome(options=option,executable_path="chromedriver.exe")
        except:
            self.dr=webdriver.Chrome(options=option,executable_path="chromedriver")

        # self.dr = webdriver.Chrome(options=(webdriver.ChromeOptions()).add_argument("headless"),executable_path="chromedriver.exe")
    def setupUi(self,MainWindow,parent=None):
        config=Config("config.ini")
        super(MyWindow,self).setupUi(MainWindow)
        self.showFilePath(config.startConfig())
        self.filePathEdit.setOpenExternalLinks(True)
        self.filePathEdit.setToolTip("点击打开文件夹")
        # self.filePathEdit.setStyleSheet("font:20pt '楷体';border-width: 1px;border-style: solid;border-color: rgb(255, 0, 0);")
        # self.downResultLable.setStyleSheet("font:20pt '宋体';border-width: 1px;border-style: solid;border-color: rgb(255, 0, 0);")
        self.searchButton.clicked.connect(self.searchSong_Thread1)
        self.selectPathButton.clicked.connect(self.filePathGet)
        #设置点击列表后的动作
        self.resultWidget.doubleClicked.connect(self.doubleClickTableDownload)
        #todo 优化1 表格填满窗口
        #水平方向标签拓展剩下的窗口部分，填满表格
        self.resultWidget.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.resultWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # 设置点击选中一行
        self.resultWidget.setSelectionBehavior(QTableWidget.SelectRows)  # 设置选中行
        # 设置表格不能被编辑
        self.resultWidget.setEditTriggers(QTableWidget.NoEditTriggers)

    def searchSong_Thread1(self):
        self.resultWidget.setRowCount(0)
        searchValue = self.searchEdit.text()
        # searchThread = threading.Thread(target=search_163music,args=(searchValue,))
        all_result=search_163music(self.dr,searchValue)
        # print(all_result)
        for i in range(len(all_result)):
            item = all_result[i]
            row = self.resultWidget.rowCount()
            self.resultWidget.insertRow(row)
            for j in range(len(item)):
                item = QTableWidgetItem(str(all_result[i][j]))
                self.resultWidget.setItem(row, j, item)
    # def isNotClicked_Thread2(self):
    #     self.searchButton.setEnabled(False)
    #     for secends in range(20,-1):
    #         self.searchButton.setText(QtCore.QCoreApplication.translate("MainWindow", secends))
    #         time.sleep(1)
    #     self.searchButton.setEnabled(True)
    #     self.searchButton.setText(QtCore.QCoreApplication.translate("MainWindow", "搜索"))

    def filePathGet(self):
        config=Config("config.ini")
        filePath = QFileDialog.getExistingDirectory(self,'open file', './')##选择文件夹
        config.set("downFilePath","path",filePath)
        self.showFilePath(config.startConfig())
    def doubleClickTableDownload(self):
        config=Config("./config.ini")
        rowNum=self.resultWidget.currentRow()
        songId=config.get("songId",str(rowNum))
        songName=config.get("songName",str(rowNum))
        downpath=config.get("downFilePath","path")
        isSuccess,isRepeat,songNameF= songDownload(songName,songId,downpath)
        if isSuccess:
            if isRepeat:
                self.downResultLable.setText("download success!! {a} is existed,it was renamed {b} ".format(a=songName,b=songNameF))
            else:
                self.downResultLable.setText(
                    "{b} download success!! ".format(b=songNameF))
        else:
            self.downResultLable.setText(
                "{b} download failed!! ".format(b=songNameF))

    def showFilePath(self,path):
        self.filePathEdit.setText("<a href={p}>{p}</a>".format(p=path))














if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())