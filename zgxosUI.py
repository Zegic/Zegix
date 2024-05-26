# # from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
# # from zos import Ui_MainWindow
# # import sys
# #
# # if __name__ == '__main__':
# #     app = QApplication(sys.argv)
# #     mainwindow = QMainWindow()
# #     ui = Ui_MainWindow()
# #     ui.setupUi(mainwindow)
# #     mainwindow.show()
# #     sys.exit(app.exec_())
# # from PyQt5 import QtWidgets
# from PyQt5.QtGui import QStandardItem
# # from PyQt5 import QtWidgets, QtCore
# from PyQt5.QtWidgets import QMainWindow,QApplication,QPushButton
# from PyQt5.uic.properties import QtWidgets
#
# from zos import Ui_MainWindow
# import sys
# from PyQt5 import *
#
#
# class DemoMain(QMainWindow,Ui_MainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)  #调用Ui_Mainwindow中的函数setupUi实现显示界面
#         self.model.setHorizontalHeaderLabels(['Item', 'Description'])
#         model = QtWidgets.QStandardItemModel(self)
#     def display_left_table(self,data:[]):
#         for row_index, row_data in enumerate(data):
#             for column_index, item_data in enumerate(row_data):
#                 item = QStandardItem(item_data)
#                 self.model.setItem(row_index, column_index, item)
#
#     def display_table_2(self,data:[]):
#         for row_data in data:
#             row_items = []
#             for item_data in row_data:
#                 item = QtWidgets.QStandardItem(item_data)
#                 row_items.append(item)
#             self.model.appendRow(row_items)
#             self.columnView.setModel(self.model)
#             self.model.setHorizontalHeaderLabels(['Item', 'Description'])
#
#
# def main():
#     app=QApplication(sys.argv)
#     mainpine=DemoMain()
#     mainpine.show()
#     testdata = [
#         ['Item 1', 'Description 1'],
#         ['Item 2', 'Description 2'],
#         ['Item 3', 'Description 3'],
#     ]
#     mainpine.display_table_2(testdata)
#     sys.exit(app.exec_())
#
#
# if __name__=='__main__':
#     main()
#
#


# 设置 model 到 QColumnView（假设你在 Ui_MainWindow 中有一个名为 columnView 的 QColumnView 控件）
# self.columnView.setModel(self.model)

# # 创建 QStandardItemModel 实例
# self.model = QStandardItemModel(self)
# self.model.setHorizontalHeaderLabels(['Item', 'Description'])
# def display_table_2(self, data: list):
#     # 清空模型（如果需要的话）
#     self.model.clear()
#
#     # 填充数据到模型中
#     for row_data in data:
#         row_items = []
#         for item_data in row_data:
#             item = QStandardItem(item_data)
#             row_items.append(item)
#         self.model.appendRow(row_items)
#
# def display_table_3(self, data: list):
#     # 清空模型
#     if isinstance(self.model, QStandardItemModel):
#         self.model.clear()
#     self.model.setHorizontalHeaderLabels(['Name', 'Priority', 'Run Time'])
#     for item_string in data:
#         parts = item_string.split('^')
#         name = parts[0]
#         priority = parts[1]
#         run_time = parts[2]
#         row_items = [
#             QStandardItem(name.strip()),  # 去除可能的首尾空格
#             QStandardItem(priority.strip()),
#             QStandardItem(run_time.strip())
#         ]
#         if isinstance(self.model, QStandardItemModel):
#             self.model.appendRow(row_items)
# def min30(self):
#     if self.remainingTime.second() == 0 and self.remainingTime.minute() == 0:
#         self.timer.stop()
#         self.lcdNumber.display("00:00")
#     self.remainingTime = self.remainingTime.addSecs(-1)
#     self.lcdNumber.display(self.remainingTime.toString("mm:ss"))
#
# def count30m(self):  # 应该调用这个函数来开始或者重置计时器
#     if not self.timer2.isActive():
#         self.timer2.start(1000)
# self.timer2 = QTimer(self)
# self.timer2.timeout.connect(self.min30)


import json
import time
from collections import namedtuple
from datetime import datetime

from PyQt5.QtCore import QTimer, QTime, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.uic import loadUi  # 假设你使用 loadUi 来加载 UI 文件
from zos import Ui_MainWindow  # 假设 zos.py 是通过 pyuic5 从 .ui 文件转换来的
import sys

PCB = namedtuple('PCB', [
    'UID',  # 进程UID
    'name',  # 进程名字，如“考研”
    'total_run_time',  # 进程所需总时间 ，按分钟单位
    'start_time',  # 进程开始的时间
    'dead_line',  # 进程截止日期
    'Status',  # 进程状态，如挂起、阻塞、就绪、运行、终止
    'Priority',  # 调度优先级，算法改变这个优先级，最终按照它来排序
    'OP',  # 原初优先级，标致一个线程的尊贵地位
    'wait',  # 这个线程等了多久
    'run_time',  # 今天的运行时间，会影响优先级调度
    'Is_Regular'])  # 是否周期任务

PCB_A_list = []
PCB_B_list = []
PAUSE = 'NO'


class DemoMain(QMainWindow, Ui_MainWindow):
    sig_hang_job = pyqtSignal(str)

    def update_time_display(self):
        current_time = QTime.currentTime()
        time = current_time.toString("hh:mm").zfill(2)  # 格式化小时并确保两位数
        self.lcdNumber.display(time)

    # 这是时钟的函数 别改错了

    def start_timer(self, str1):
        if not self.timer2.isActive():
            it = int(str1)
            self.remaining_time = QTime(0, it, 0)  # 重置为30分钟
            self.timer2.start(1000)  # 每秒更新一次

    def reset_timer(self, str1):
        # print(str1)
        self.timer2.stop()
        it = int(str1)
        self.remaining_time = QTime(0, it, 0)
        self.start_timer(str1)

    def pause_timer(self):
        if self.timer2.isActive():
            self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer2.stop()
            # else:
            self.timer2.start(1000)

    # 显示LCD倒计时的函数
    def update_timer(self):
        # print("1")
        if not self.is_paused:
            if self.remaining_time.second() > 0:
                self.remaining_time = self.remaining_time.addSecs(-1)
            else:
                if self.remaining_time.minute() > 0:
                    self.remaining_time = self.remaining_time.addSecs(-60)
                    self.remaining_time = QTime(self.remaining_time.hour(), self.remaining_time.minute() - 1, 59)
            if self.remaining_time.second() == 0 and self.remaining_time.minute() == 0:
                self.timer2.stop()
            else:
                # time = QTimer.toString("hh:mm").zfill(2)  # 格式化小时并确保两位数
                # self.remaining_time
                time = self.remaining_time.toString("mm:ss")
                # print(time)
                self.lcdNumber_2.display(time)

    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 调用 Ui_Mainwindow 中的 setupUi 方法实现显示界面

        # 倒计时30min
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.update_timer)
        self.remaining_time = QTime(0, 30, 0)  # 30分钟
        self.is_paused = False
        self.start_timer("30")
        self.reset_timer("30")
        # 表格
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['名称', '优先级', '运行时间'])
        self.remainingTime = QTime(0, 30)

        # 显示时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_display)
        self.timer.start(1000)
        self.update_time_display()

        # 完成任务按钮
        self.pushButton.clicked.connect(self.finish_job)
        # 创建进程按钮
        self.pushButton_4.clicked.connect(self.create_job)
        # 保存
        self.pushButton_5.clicked.connect(self.write_to_file)
        # 暂停
        self.pushButton_2.clicked.connect(self.pause)
        # 挂起
        self.pushButton_3.clicked.connect(self.hang_job)

    def pause(self):
        global PAUSE
        if PAUSE == 'NO':
            PAUSE = 'YES'
        elif PAUSE == 'YES':
            PAUSE = 'NO'
        self.pause_timer()

    def write_to_file(self):
        with open('appdata.txt', 'w') as f:
            for pcb in PCB_B_list:
                pcb_dict = pcb._asdict()
                json.dump(pcb_dict, f)
                f.write('\n')

    def create_job(self):
        now = datetime.now()
        formatted_time = now.strftime('%Y%m%d%H%M%S')
        pname = '新任务'
        if self.textEdit.toPlainText():
            pname = self.textEdit.toPlainText()
        starttime = now.strftime('%Y-%m-%d,%H:%M')
        ddl = ''
        if self.textEdit_2.toPlainText():
            ddl = self.textEdit_2.toPlainText()
        pr = 50
        OP = 50
        if self.textEdit_3.toPlainText():
            pr = int(self.textEdit_3.toPlainText())
            OP = pr

        p = PCB(UID=formatted_time, name=pname, total_run_time=60, start_time=starttime, dead_line=ddl, Status='Ready',
                OP=OP, Priority=pr, wait=0, run_time=0, Is_Regular='NO')
        PCB_B_list.append(p)

    def hang_job(self):
        self.sig_hang_job.emit("hang")
        pass

    def finish_job(self):
        if PCB_B_list:
            PCB_B_list.pop(0)

    @pyqtSlot(str)
    def update_doing(self, text):
        self.textBrowser_3.setPlainText(text)

    def set_table(self, data: list):
        self.tableWidget.setRowCount(0)
        for row_index, row_data in enumerate(data):
            self.tableWidget.insertRow(row_index)
            for col_index, item_data in enumerate(row_data):
                item = QTableWidgetItem(item_data)
                self.tableWidget.setItem(row_index, col_index, item)


class UpdateTable(QThread):
    update_signal = pyqtSignal(list)  # 定义一个信号用于发送更新数据
    update_text_signal = pyqtSignal(str)
    update_clock = pyqtSignal(str)
    Hang = 'NO'

    def __init__(self, pcb_list):
        super().__init__()
        self.pcb_list = pcb_list

    def hang_process(self, str):
        self.Hang = 'YES'
        print(str)
        print(self.Hang)
        # 挂起程序，立即将PCB重排序，立即重置倒计时，下次运行时，倒计时要等于进程剩下的倒计时
        # 挂起程序，设置挂起信号量，
    def dismin(self,seconds):
        # 计算分钟和秒
        minutes, remainder = divmod(seconds, 60)
        # 将秒数转换为两位数的字符串，如果不足两位数则前面补0
        seconds_str = str(remainder).zfill(2)
        # 返回分钟和秒的字符串格式
        return "{:02d}:{}".format(minutes, seconds_str)

    def run(self):
        if PCB_B_list:
            self.update_clock.emit(str((30 * 60 - PCB_B_list[0].run_time) // 60))
        stime = 0
        while True:
            if PAUSE == 'NO':
                stime += 1
                time.sleep(1)  # 在这里变速
                if PCB_B_list:  # 如果列表不为空
                    if PCB_B_list[0].run_time >= 30 * 60:
                        PCB_B_list[0] = PCB_B_list[0]._replace(Status='Ready', run_time=0)
                        PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
                        self.update_clock.emit(str((30 * 60 - PCB_B_list[0].run_time) // 60))
                    if self.Hang == 'YES':
                        if PCB_B_list:
                            self.update_clock.emit(str((30 * 60 - PCB_B_list[0].run_time) // 60))
                            PCB_B_list[0] = PCB_B_list[0]._replace(Status='Ready')
                            tmp = PCB_B_list[0]
                            PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
                            if tmp == PCB_B_list[0]:
                                if PCB_B_list[1]:
                                    PCB_B_list[0] = PCB_B_list[1]
                                    PCB_B_list[1] = tmp

                        self.Hang = 'NO'
                    if PCB_B_list:  # 再次检查列表，以防在删除后为空
                        # 当前运行任务进行特殊处理，注意sort的位置，否则会导致时间片不满就切换

                        first = PCB_B_list.pop(0)
                        PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)
                        first = first._replace(Status='Run', Priority=first.OP,
                                               run_time=first.run_time + 1)
                        # 更新任务详情
                        text_to_display = "任务信息：\n名称：" + str(first.name) + "\n优先级" + str(
                            ("%.1f" % first.Priority)) + "\n状态：" + str(first.Status) + "\n已运行时间：" + str(
                            self.dismin(int(first.run_time))) + "\n创建时间：" + str(first.start_time) + "\n是否周期任务：" + str(
                            first.Is_Regular)
                        # print(text_to_display)
                        self.update_text_signal.emit(text_to_display)
                        # 组合为表输出
                        for i, p in enumerate(PCB_B_list):
                            if stime % 60 == 0:
                                PCB_B_list[i] = p._replace(Status='Ready', Priority=p.Priority * 1.009)
                        PCB_B_list.insert(0, first)
                        display_data = []  # 将来要用来AB混合
                        for p in PCB_B_list:
                            display_data.append([str(p.name), str(("%.1f" % p.Priority)), str(self.dismin(int(p.run_time)))])
                        self.update_signal.emit(display_data)
                        # DemoMain.set_table(display_data)
            else:
                time.sleep(1)


def main():
    app = QApplication(sys.argv)
    mainpine = DemoMain()
    mainpine.show()

    load = read_from_file("appdata.txt")
    PCB_B_list.extend(load)
    PCB_B_list.sort(key=lambda x: x.Priority, reverse=True)

    thread_update_table = UpdateTable(PCB_B_list)
    thread_update_table.update_signal.connect(mainpine.set_table)
    thread_update_table.update_text_signal.connect(mainpine.update_doing)
    thread_update_table.update_clock.connect(mainpine.reset_timer)
    mainpine.sig_hang_job.connect(thread_update_table.hang_process)
    thread_update_table.start()

    sys.exit(app.exec_())


def read_from_file(filename):
    pcbs = []
    with open(filename, 'r') as f:
        for line in f:
            # 从文件中读取并解析字典
            pcb_dict = json.loads(line)
            # 使用PCB namedtuple从字典创建实例
            pcb = PCB(**pcb_dict)
            pcbs.append(pcb)
    return pcbs


def write_to_file(filename, pcbs):
    with open(filename, 'w') as f:
        for pcb in pcbs:
            # 将PCB实例转换为字典，因为json不能直接处理namedtuple
            pcb_dict = pcb._asdict()
            json.dump(pcb_dict, f)
            f.write('\n')  # 在每个PCB字典后添加换行符以便分隔


if __name__ == '__main__':
    main()

# 现在的任务：创建新pcb
# 之后的任务：
# 做出时间的流失
# 绑定按钮
# 剩余时间
# 2 算法，写出双队列
# 2,写出功能：，调整文件读取，
# 3，做出线程，做出线程安全，做出非阻塞
# 3，优化GUI，加一个切换进程后发出声音来提示，比如叮咚
# 想一个更好的调度算法
