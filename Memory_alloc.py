# from io import RawIOBase
import sys, os
# if hasattr(sys, 'frozen'):
#     os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

# from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
# import platform
import ctypes
import Mem_alloc
from Mem_alloc import *
import copy
# import random
import math
import Memory_Allocator
# import memory_allocator_rc
# from memory_allocator_rc import *

# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

from PyQt5.uic import loadUiType

Memory_Allocator, _ = loadUiType('Memory_Allocator.ui')


class MainApp(QMainWindow, Memory_Allocator):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.onlyInt = QIntValidator()
        self.setupUi(self)
        self.ui = Memory_Allocator
        self.restrict_input()
        self.handle_buttons()
        self.add_hole.setEnabled(False)
        self.next.setEnabled(False)
        self.ok.setEnabled(False)
        self.compaction.setEnabled(False)
        self.ok_memory.setEnabled(False)
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.move(centerPoint.x() - int(self.width() / 2), centerPoint.y() - int(self.height() / 2))
        # self.hole_table.setSizeAdjustPolicy(self.QtWidgets.QAbstractScrollArea.AdjustToContents)

    ############################################################
    # buttons connection to pages ##############################
    def handle_buttons(self):
        # self.hole_table.resizeColumnsToContents()
        self.next.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.back.clicked.connect(lambda: self.back_handler())
        self.add_hole.clicked.connect(lambda: self.handle_hole_edits())
        self.delete_hole.clicked.connect(lambda: self.delete_hole_handler())
        self.next.clicked.connect(lambda: self.next_handler())
        self.ok.clicked.connect(lambda: self.ok_handler())
        self.add_process.clicked.connect(lambda: self.add_process_handler())
        self.delete_process.clicked.connect(lambda: self.delete_process_handler())
        self.compaction.clicked.connect(lambda: self.compaction_handler())
        self.ok_memory.clicked.connect(lambda: self.ok_memory_handler())

        self.no_of_segments.textChanged.connect(lambda: self.disable_buttons())
        self.memory_size.textChanged.connect(lambda: self.disable_buttons())
        self.starting_address.textChanged.connect(lambda: self.disable_buttons())
        self.hole_size.textChanged.connect(lambda: self.disable_buttons())

        # ewturn pressed
        self.memory_size.returnPressed.connect(self.ok_memory.click)
        self.hole_size.returnPressed.connect(self.add_hole.click)
        self.no_of_segments.returnPressed.connect(self.ok.click)
        self.starting_address.returnPressed.connect(lambda: self.hole_size.setFocus())

        self.show()

    ###########################################################
    # Restrictions ############################################

    # disable buttons if no text
    def disable_buttons(self):
        self.add_hole.setEnabled(False)
        self.ok.setEnabled(False)
        self.ok_memory.setEnabled(False)
        if (len(self.memory_size.text()) > 0 and len(self.starting_address.text()) > 0) and len(
                self.hole_size.text()) > 0:
            self.add_hole.setEnabled(True)
        # if len(self.memory_size.text()) > 0:
        #     self.next.setEnabled(True)
        if len(self.no_of_segments.text()) > 0:
            self.ok.setEnabled(True)
        if len(self.memory_size.text()) > 0:
            self.ok_memory.setEnabled(True)

    ##restrict lineEdits only on integers
    def restrict_input(self):
        self.memory_size.setValidator(self.onlyInt)
        self.starting_address.setValidator(self.onlyInt)
        self.hole_size.setValidator(self.onlyInt)
        self.no_of_segments.setValidator(self.onlyInt)

    ###########################################################
    # Button handlers #########################################
    def ok_memory_handler(self):
        Mem_alloc.Mem_size = int(self.memory_size.text())
        self.starting_address.setFocus()
        if Mem_alloc.Mem_size != 0:
            self.next.setEnabled(True)
            generate_old_procs()
            # filling the process table with all processes
            self.update_process_table()
            self.chart()
            self.compaction.setEnabled(False)
            if len(Mem_alloc.holes) > 0:
                self.compaction.setEnabled(True)
        else:
            ctypes.windll.user32.MessageBoxW(0, "You entered zero sized memory.", "Error", 1)

    def handle_hole_edits(self):
        Mem_alloc.Mem_size = int(self.memory_size.text())

        hole_start = int(self.starting_address.text())
        hole_size = int(self.hole_size.text())

        # check proposed Hole range validity
        hole_valid = 1  # flag
        for h in list(Mem_alloc.holes):
            s0 = hole_start  # proposed hole start
            e0 = hole_start + hole_size  # proposed hole end
            s1 = h['start']  # current hole start
            e1 = h['start'] + h['size']  # current hole end
            if s0 - e1 < 0 and s1 - e0 < 0:
                hole_valid = 0
                # ctypes.windll.user32.MessageBoxW(0, "Proposed hole is out of valid range.", "Error", 1)
                break

        if (hole_start + hole_size <= Mem_alloc.Mem_size and hole_valid == 1) and hole_size != 0:
            Mem_alloc.holes.append({'name': "", 'start': int(hole_start), 'size': int(hole_size)})
            generate_old_procs()
            # filling the process table with all processes
            self.update_process_table()
            # update gantt chart
            self.chart()

            self.hole_table.setRowCount(int(len(Mem_alloc.holes)))
            for i in range(len(Mem_alloc.holes)):
                self.hole_table.setItem(i, 0, QTableWidgetItem(str(Mem_alloc.holes[i]['start'])))
                self.hole_table.setItem(i, 1, QTableWidgetItem(str(Mem_alloc.holes[i]['size'])))

            self.starting_address.clear()
            self.hole_size.clear()
            self.starting_address.setFocus()
        else:
            if hole_size == 0:
                ctypes.windll.user32.MessageBoxW(0, "You entered a zero sized hole.", "Error", 1)
            else:
                ctypes.windll.user32.MessageBoxW(0, "Proposed hole is out of valid range.", "Error", 1)
        self.next.setEnabled(False)
        self.compaction.setEnabled(False)
        if len(Mem_alloc.holes) > 0:
            self.next.setEnabled(True)
            self.compaction.setEnabled(True)

        width = self.hole_table.horizontalHeader().length()
        if width <= 300:
            # header = self.hole_table.horizontalHeader()
            # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            if self.hole_table.verticalScrollBar().isVisible():
                width += self.hole_table.verticalScrollBar().width()
        width += 20
        self.hole_table.setFixedWidth(width)

    def ok_handler(self):
        if int(self.no_of_segments.text()) == 0:
            ctypes.windll.user32.MessageBoxW(0, "You entered zero sized memory.", "Error", 1)
        else:
            # determine the allocation algorithm
            if self.first_fit.isChecked():
                Mem_alloc.algo = 'f'
            elif self.best_fit.isChecked():
                Mem_alloc.algo = 'b'
            elif self.worst_fit.isChecked():
                Mem_alloc.algo = 'w'

            Mem_alloc.seg_num = int(self.no_of_segments.text())
            self.segments_table.setRowCount(int(Mem_alloc.seg_num))

            self.segments_table.setFocus()

    def add_process_handler(self):
        self.no_of_segments.setFocus()
        Mem_alloc.added_process_status = "fit"
        if self.segments_table.rowCount() > 0:
            try:
                if Mem_alloc.added_process_status == "fit":
                    # determine the allocation algorithm
                    if self.first_fit.isChecked():
                        Mem_alloc.algo = 'f'
                    elif self.best_fit.isChecked():
                        Mem_alloc.algo = 'b'
                    elif self.worst_fit.isChecked():
                        Mem_alloc.algo = 'w'

                    # insert a process
                    Mem_alloc.current_proc = []
                    # inputs
                    for i in range(int(Mem_alloc.seg_num)):
                        seg_name = self.segments_table.item(i, 0).text()
                        seg_size = self.segments_table.item(i, 1).text()
                        if seg_name == "":
                            Mem_alloc.current_proc = []
                            ctypes.windll.user32.MessageBoxW(0, "Data entered is incomplete or invalid.", "Error", 1)
                            break
                        Mem_alloc.current_proc.append(
                            {'pid': "P" + str(Mem_alloc.index), 'name': seg_name, 'start': 0, 'size': int(seg_size)})

                    # output
                    insert_process()
                    # filling the process table with all processes
                    self.update_process_table()
                    # update gantt chart
                    self.chart()

            except Exception as e:
                ctypes.windll.user32.MessageBoxW(0, "Data entered is incomplete or invalid.", "Error", 1)

            # check if compaction can helps if process cannot fit
            if Mem_alloc.added_process_status == "not fit":
                process_size = 0
                for s in list(Mem_alloc.current_proc):
                    process_size += s['size']

                hole_sum = 0
                for h in list(Mem_alloc.holes):
                    hole_sum += h['size']

                if process_size <= hole_sum:
                    Mem_alloc.added_process_status = "fit"
                    msgbox = QMessageBox()
                    msgbox.setWindowTitle("Error")
                    msgbox.setText("This process does not fit, but compaction can help!\n")
                    msgbox.addButton(msgbox.No)
                    applyCompaction = msgbox.addButton("       Apply compaction, and Allocte      ", msgbox.YesRole)
                    applyCompaction.clicked.connect(lambda: self.msg_action())
                    bttn = msgbox.exec_()
                    msgbox.close()

                else:
                    ctypes.windll.user32.MessageBoxW(0, "This process does not fit.", "Error", 1)

            if Mem_alloc.added_process_status == "not fit 0":
                ctypes.windll.user32.MessageBoxW(0, "You entered zero sized segments.", "Error", 1)
                # Mem_alloc.processes.pop(-1)
                memory_alloc()
                self.update_process_table()

        else:
            ctypes.windll.user32.MessageBoxW(0, "No process to allocate.", "Error", 1)
        self.no_of_segments.setFocus()

    def delete_process_handler(self):
        self.no_of_segments.setFocus()
        try:
            row = self.process_table.currentRow()
            proc = self.process_table.item(row, 0).text()

            de_allocate(proc)
            # filling the process table with all processes
            self.update_process_table()
            # update gantt chart

            self.chart()
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, "Please, select a process to de-allocate.", "Error", 1)

        self.process_table.setCurrentItem(None)

    def delete_hole_handler(self):
        self.starting_address.setFocus()
        try:
            memory.clear()
            # hole = self.hole_table.currentItem().text()
            row = self.hole_table.currentRow()
            hole = self.hole_table.item(row, 0).text()
            for i in range(len(Mem_alloc.holes)):
                if Mem_alloc.holes[i]['start'] == int(hole):
                    Mem_alloc.holes.pop(i)
                    break
            if len(Mem_alloc.holes) == 0: self.hole_table.setRowCount(0)
            self.hole_table.setRowCount(int(len(Mem_alloc.holes)))
            for i in range(len(Mem_alloc.holes)):
                self.hole_table.setItem(i, 0, QTableWidgetItem(str(Mem_alloc.holes[i]['start'])))
                self.hole_table.setItem(i, 1, QTableWidgetItem(str(Mem_alloc.holes[i]['size'])))

            generate_old_procs()
            # filling the process table with all processes
            self.update_process_table()
            # update gantt chart
            self.chart()

            # self.hole_table.clearSelection()
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, "Please, select a hole to de-allocate.", "Error", 1)
        self.hole_table.setCurrentItem(None)

        self.next.setEnabled(False)
        self.compaction.setEnabled(False)
        if len(Mem_alloc.holes) > 0:
            self.next.setEnabled(True)
            self.compaction.setEnabled(True)

        # header = self.hole_table.horizontalHeader()
        # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        width = self.hole_table.horizontalHeader().length()
        if width <= 400:
            if self.hole_table.verticalScrollBar().isVisible():
                width += self.hole_table.verticalScrollBar().width()
            width += 5
            self.hole_table.setFixedWidth(width)

    global OldPColor
    OldPColor = "#f94144"
    global page
    page = 0

    def back_handler(self):
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Warning! New entry")
        msgbox.setText("All data will be lost!\n\nAs, it's not allowed to re-define holes.\n")
        ok_bttn = msgbox.addButton("       Ok      ", msgbox.YesRole)
        ok_bttn.clicked.connect(lambda: self.back_action())
        cancel_bttn = msgbox.addButton("       Cancel      ", msgbox.NoRole)
        # cancel_bttn.clicked.connect(lambda: self.back_action())
        bttn = msgbox.exec_()
        msgbox.close()

    def back_action(self):
        self.stackedWidget.setCurrentWidget(self.page_1)
        Mem_alloc.holes.clear()
        Mem_alloc.segments.clear()
        Mem_alloc.processes.clear()
        Mem_alloc.index = 0
        Mem_alloc.memory.clear()
        Mem_alloc.color_picker.clear()
        Mem_alloc.added_process_status = "fit"

        self.memory_size.clear()
        self.starting_address.clear()
        self.hole_size.clear()
        self.no_of_segments.clear()
        self.hole_table.setRowCount(0)
        self.segments_table.setRowCount(0)
        self.process_table.setRowCount(0)

        self.memory_size.setFocus()
        self.memory.setScene(None)
        self.memory.show()

        self.compaction.setEnabled(False)
        self.next.setEnabled(False)
        global OldPColor
        OldPColor = "#f94144"
        global page
        page = 0

    def next_handler(self):
        if Mem_alloc.Mem_size == 0 and len(Mem_alloc.memory) == 0:
            generate_old_procs()
        self.update_process_table()
        self.no_of_segments.setFocus()
        global OldPColor
        OldPColor = "#FFFFFF"
        self.chart()
        global page
        page = 1

    def compaction_handler(self):
        self.no_of_segments.setFocus()
        apply_compaction()
        # filling the process table with all processes
        global page
        if page == 0: generate_old_procs()
        # filling the process table with all processes
        self.update_process_table()
        # update gantt chart
        self.chart()

        self.hole_table.setRowCount(int(len(Mem_alloc.holes)))
        for i in range(len(Mem_alloc.holes)):
            self.hole_table.setItem(i, 0, QTableWidgetItem(str(Mem_alloc.holes[i]['start'])))
            self.hole_table.setItem(i, 1, QTableWidgetItem(str(Mem_alloc.holes[i]['size'])))

    #############################################################
    # Helper functions ##########################################
    def update_process_table(self):
        if len(Mem_alloc.holes) > 0:
            self.compaction.setEnabled(True)
        else:
            self.compaction.setEnabled(False)
        if len(Mem_alloc.processes) == 0: self.process_table.setRowCount(0)
        for i in range(len(Mem_alloc.processes)):
            self.process_table.setRowCount(int(len(Mem_alloc.processes)))
            self.process_table.setItem(i, 0, QTableWidgetItem(str(Mem_alloc.processes[i]['pid'])))
            self.process_table.setItem(i, 1, QTableWidgetItem(str(Mem_alloc.processes[i]['seg_num'])))
            self.process_table.setItem(i, 2, QTableWidgetItem(str(Mem_alloc.processes[i]['seg_info'])))
            color = ""
            if Mem_alloc.processes[i]['pid'][0:3] == "Old":
                color = "#f94144"
            else:
                color = Mem_alloc.color_picker[i]
            self.process_table.item(i, 0).setBackground(QBrush(QColor(color)))
            self.process_table.item(i, 1).setBackground(QBrush(QColor(color)))
            self.process_table.item(i, 2).setBackground(QBrush(QColor(color)))

            header = self.process_table.horizontalHeader()
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            width = self.process_table.horizontalHeader().length()
            if width <= 700:
                if self.process_table.verticalScrollBar().isVisible():
                    width += self.process_table.verticalScrollBar().width()
                width += 20
                self.process_table.setFixedWidth(width)
            else:
                self.process_table.setMaximumWidth(5000)

            header2 = self.segments_table.horizontalHeader()
            header2.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            width2 = self.segments_table.horizontalHeader().length()
            if width2 <= 700:
                if self.segments_table.verticalScrollBar().isVisible():
                    width2 += self.segments_table.verticalScrollBar().width()
                width2 += 15
                self.segments_table.setFixedWidth(width2)
            else:
                self.segments_table.setMaximumWidth(10000)

    def msg_action(self):

        apply_compaction()
        self.add_process_handler()

    ############################################################
    # Gantt chart ##############################################
    def chart(self):
        scene = QGraphicsScene()
        whiteBrush = QBrush(Qt.white)
        shadowBrush = QBrush(QColor("#353535"))
        redBrush = QBrush(QColor("#f94144"))
        # randomBrrush = QBrush(QColor(random.choice(colors)))
        # grayPen = QPen(Qt.gray)
        grayPen = QPen(QColor("#495057"))
        grayPen.setWidth(1)
        # random color for every process
        processes_pids = []
        for p in list(Mem_alloc.processes):
            processes_pids.append(p['pid'])

        # draw
        # f = 468 / Mem_alloc.Mem_size  # drawing factor
        f = 624 / Mem_alloc.Mem_size  # drawing factor
        if len(Mem_alloc.memory):
            memory_copy = copy.deepcopy(Mem_alloc.memory)
            memory_copy.sort(key=size_)
            if memory_copy[0]['size'] * f < 35:
                f = 35 / memory_copy[0]['size']
            del memory_copy
        location = 0
        lst = []
        lst = Mem_alloc.memory if Mem_alloc.memory and Mem_alloc.Mem_size != 0 else [
            {'pid': "Old Process", 'name': "", 'start': 0, 'size': Mem_alloc.Mem_size}]
        for s in list(lst):
            location = s['start']
            # Rectangles
            if s['name'][0:4] == "Hole":
                rect = scene.addRect(135, location * f, 200, s['size'] * f, grayPen, shadowBrush)
                item = scene.addText(s['name'], QFont('Arial', 13))
                item.setDefaultTextColor(QColor("#FFFFFF"))
                lengthh = 0
                for c in str(s['name']):
                    lengthh += 1
                item.setPos(135 + 100 - (lengthh / 2) * 10, (location + s['size'] / 2) * f - 14)
                # item.setPos(192, (location + s['size'] / 2) * f - 14)

            elif s['pid'][0:3] == "Old":
                rect = scene.addRect(135, location * f, 200, s['size'] * f, grayPen, redBrush)
                item = scene.addText(s['pid'] + " " + s['name'], QFont('Arial', 13))
                item.setDefaultTextColor(QColor(OldPColor))
                lengtho = 0
                for c in str(s['pid'] + " " + s['name']):
                    lengtho += 1
                item.setPos(135 + 110 - (lengtho / 2) * 10, (location + s['size'] / 2) * f - 14)

            else:
                ind = 0
                for i in range(len(processes_pids)):
                    if s['pid'] == processes_pids[i]: ind = i
                rect = scene.addRect(135, location * f, 200, s['size'] * f, grayPen,
                                     QBrush(QColor(Mem_alloc.color_picker[ind])))
                # rect = scene.addRect(130, location * f, 170, s['size'] * f, redPen, whiteBrush)
                item = scene.addText(s['pid'] + " " + s['name'], QFont('Arial', 13))
                item.setDefaultTextColor(QColor("#000000"))
                length = 0
                for c in str(s['pid'] + " " + s['name']):
                    length += 1
                item.setPos(135 + 100 - (length / 2) * 8, (location + s['size'] / 2) * f - 14)

            # Locations
            lengthl = 0
            for c in str(location):
                lengthl += 1
            item = scene.addText(str(location), QFont('Arial', 11))
            item.setPos(130 - lengthl * 10, location * f - 12)
            location += s['size']

        # Memory end location
        item = scene.addText(str(location), QFont('Arial', 11))
        item.setPos(130 - int(math.log10(float(location + 9)) + 1) * 10, location * f - 12)
        self.memory.setScene(scene)
        self.memory.show()


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()
    input()


if __name__ == '__main__':
    main()
