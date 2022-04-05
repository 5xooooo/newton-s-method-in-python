from math import ceil
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QMessageBox, QDesktopWidget)
from ui import Ui_MainWindow
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime


# label = 請輸入實係數多項式
# label_3 = f(x) = 
# label_4 = 選擇根
# label_5 = 近似次數
# label_6 = 近似值
# linedit = 輸入框
# pushbutton_2 = 下一次近似
# pushbutton_3 = 輸出圖形
# pushbutton_4 = 確定
# combobox = 根清單 


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.label.setFont(QtGui.QFont('Microsoft JhengHei', 15))
        self.ui.label_2.setFont(QtGui.QFont('Microsoft JhengHei', 10))
        self.ui.label_3.setFont(QtGui.QFont('Microsoft JhengHei', 10))
        self.ui.label_4.setFont(QtGui.QFont('Microsoft JhengHei', 15))

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 5, (screen.height() - size.height()) // 3) 

        self.ui.pushButton_4.clicked.connect(self.comfirm_clicked)
        self.ui.pushButton_2.clicked.connect(self.next)
        self.ui.pushButton_3.clicked.connect(self.output_image)
        self.ui.comboBox.currentIndexChanged.connect(self.index_changed)
        self.coe_dict = {}
        self.deg = 0
        self.df_dict = {}
        plt.ion()

    def warning(self, msg) -> None:
        reply = QMessageBox.warning(self, '錯誤訊息', msg,
            QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)

    def process_input(self) -> None:
        text = self.ui.lineEdit.text()
        self.title = text
        self.coe_dict.clear()
        try:
            content = text.split('+')
            for i in content:
                if i != '':
                    if 'x^' in i: #分離係數及次數並存在coe_dict中
                        coe = i.split('x^')
                        if coe[0] == '': 
                            self.coe_dict[int(coe[1])] = 1
                        elif coe[0] == '-': 
                            self.coe_dict[int(coe[1])] = -1
                        else:
                            self.coe_dict[int(coe[1])] = int(coe[0])
                    elif 'x' in i: #處理係數為1的情況
                        if len(i) == 1:
                            self.self.coe_dict[1] = 1
                        else:
                            self.coe_dict[1] = int(i[:-1])
                    else: #處理常數項
                        self.coe_dict[0] = int(i)
        except:
            self.warning("輸入的格式有誤")
        
    def output_data(self) -> None:
        self.deg = max(self.coe_dict) #最高次項係數deg

        for key in range(self.deg+1):
            self.coe_dict.setdefault(key, 0) #補齊缺漏的係數0

        df = self.diff(self.coe_dict) #df = 微分到一次後係數dict
        if df[1] == 0:
            self.mid = 0
        else:
            self.mid = df[0]*-1/df[1]
        self.realroots = self.find_roots()

        try:
            left = min(self.realroots)
            right = max(self.realroots) #在實根中找出最大最小值以便找出繪圖區域
            self.d = max(abs(self.mid-left), abs(right-self.mid))
            if abs(round(self.d)) == 0:
                self.d = 5
        except Exception as e:
            self.d = 0
        self.plotimage(round(self.mid-self.d)-2, round(self.mid+self.d)+2, ppr=10)

    def find_roots(self) -> list:
        try:
            self.coe = []
            deg = max(self.coe_dict)
            for key in range(deg, -1, -1):
                self.coe.append(self.coe_dict[key]) #self.coe = 係數陣列
            roots_ = np.roots(self.coe) #求根
            print(roots_)
        except:
            return []
        realroots = []
        for i in roots_:#找出實根
            if np.imag(i) == 0:
                int_ = True
                t = str(np.real(i)).split('.')[1]
                for j in range(10):
                    if t[j] != '9':
                        int_ = False
                        break
                if int_:
                    realroots.append(round(np.real(i)))
                else:
                    realroots.append(float(i))
                int_ = True
        return realroots

    def diff(self, dic:dict) -> dict:
        tmp = {}
        if self.deg == 1: 
            return dic
        else:
            try:
                for i in range(self.deg, 0, -1):
                    tmp[i-1] = dic[i] * i
                self.deg -= 1
                return self.diff(tmp)
            except:
                self.warning('請輸入最高次項係數>=2的函數 :(')        

    def comfirm_clicked(self) -> None:
        self.process_input()
        self.output_data()
        self.ui.comboBox.clear()
        self.ui.comboBox.addItem('選擇實根')
        self.add_item()
        self.approximate_times = 0

    def plotimage(self, left, right, ppr) -> None:
        length = (right - left)*ppr
        self.x = []
        self.y = []
        for i in range(length):
            self.x.append(round(left + i/ppr, 5))
        for i in range(length):
            num = 0
            for j in range(len(self.coe_dict)):
                num += self.coe_dict[j] * (self.x[i] ** j)
            self.y.append(round(num, 5))

        # plt.ion()
        try:
            plt.clf()
            plt.close()
        except:
            pass

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        ax.xaxis.set_ticks_position('bottom')
        ax.spines['bottom'].set_position(('data', 0))
        ax.yaxis.set_ticks_position('left')
        ax.spines['left'].set_position(('data', 0))

        line, = ax.plot(self.x, self.y)
        # ax.plot([10, 10])
        line.set_xdata(self.x)
        line.set_ydata(self.y)
        for i in self.realroots:
            plt.scatter(i, 0)
            plt.annotate('({}, 0)'.format(round(i, 5)), (i, 0))
        fig.canvas.draw()
        plt.get_current_fig_manager().window.setGeometry(1000, 100, 800, 800)

    def add_item(self) -> None:
        for i in range(len(self.realroots)):
            f = ceil(self.realroots[i])
            b = f-1
            text = '{} < r{} < {}'.format(str(b), i+1, str(f))
            self.ui.comboBox.addItem(text)

    def find_value(self, index_) -> None :
        key = self.x.index(index_)
        return self.y[key]

    def next(self) -> None:
        try:
            if self.approximate_times == 0:
                self.previousx = int(self.ui.comboBox.currentText().split('<')[2][1:]) +3
            y = 0
            for i in range(len(self.coe_dict)):
                y += self.coe_dict[i] * (self.previousx ** i)
            y_horizontalrange = []
            for i in range(round(y*10)):
                y_horizontalrange.append(i/10)
            x_verticalrange = [self.previousx]*round(y*10)
            plt.plot(x_verticalrange, y_horizontalrange)
            plt.scatter(self.previousx, y)

            for i in range(max(self.coe_dict), 0, -1):
                self.df_dict[i-1] = self.coe_dict[i] * i #一次微分後係數字典

            self.slope = 0
            for i in range(max(self.df_dict), -1, -1):
                self.slope += self.df_dict[i] * (self.previousx ** i)

            """ 點斜式
                y - y1 = m(x - x1)
                y - y1 = mx - mx1
                mx = y - y1 + mx1
                x = (y - y1 - mx1)/m
                x截距 : y  = 0
                x = (-y1/m) - x1
            """
            self.currentx = (-y/self.slope) + self.previousx

            length = round(10 *(abs(self.previousx-self.currentx)+2))
            if self.previousx > self.currentx:
                x_range = np.linspace(self.currentx-1, self.previousx+1, length)
            else:
                x_range = np.linspace(self.previousx-1, self.currentx+1, length)

            y_range = self.slope*x_range - self.slope*self.currentx
            plt.plot(x_range, y_range)
            self.previousx = self.currentx
        
        except:
            self.warning('請選擇欲近似的根')
        
        self.approximate_times += 1
        self.ui.label_5.setText('近似次數 : {}'.format(str(self.approximate_times)))
        self.ui.label_6.setText('近似值 : {}'.format(str(self.currentx)))

    def index_changed(self):
        self.approximate_times = 0
        self.currentx = 0
        self.previousx = 0
        self.ui.label_5.setText('近似次數 : 0')
        self.ui.label_6.setText('近似值 : None')

    def output_image(self):
        name = str(datetime.datetime.now()).split('.')[0].replace(' ', '_')
        plt.savefig('figure.png')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 

#https://clay-atlas.com/blog/2019/08/26/python-chinese-pyqt5-tutorial-install/