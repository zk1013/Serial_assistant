import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QDesktopWidget, QGroupBox,
                             QGridLayout, QTextBrowser, QVBoxLayout, QFormLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox, QTextEdit,
                             QLineEdit, QHBoxLayout)
from PyQt5.QtCore import QDateTime, QTimer, QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator


class SerialUi(QWidget):
    def __init__(self):
        super().__init__()
        # 初始化UI
        self.unit_ui()

    # 初始化UI
    def unit_ui(self):
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.set_serial_setting_groupbox(), 0, 0)
        grid_layout.addWidget(self.set_serial_state_groupbox(), 1, 0)
        grid_layout.addWidget(self.set_receive_groupbox(), 0, 1)
        self.setLayout(grid_layout)
        self.resize(760, 420)
        self.setWindowIcon(QIcon('title_icon.png'))
        self.center()
        self.setWindowTitle('iPhone Checker')
        # self.setFixedSize(760, 450)
        self.show()

    # 串口设置 区
    def set_serial_setting_groupbox(self):
        # 设置一个 串口设置 分组框
        serial_setting_gb = QGroupBox('串口设置')
        # 创建 串口设置 分组框内的布局管理器
        serial_setting_formlayout = QFormLayout()

        # 检测串口 按钮
        self.sset_btn_detect = QPushButton('检测串口')
        serial_setting_formlayout.addRow('串口选择：', self.sset_btn_detect)

        # 选择串口 下拉菜单
        self.sset_cb_choose = QComboBox(serial_setting_gb)
        serial_setting_formlayout.addRow(self.sset_cb_choose)

        # 波特率 下拉菜单
        self.sset_cb_baud = QComboBox(serial_setting_gb)
        self.sset_cb_baud.addItems(['100', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200',
                          '38400', '56000', '57600', '115200', '128000', '256000'])
        # self.sset_cb_baud.setCurrentIndex(12)
        serial_setting_formlayout.addRow('波特率：', self.sset_cb_baud)

        # 数据位 下拉菜单
        self.sset_cb_data = QComboBox(serial_setting_gb)
        self.sset_cb_data.addItems(['8', '7', '6', '5'])
        # self.sset_cb_data.setCurrentIndex(0)
        serial_setting_formlayout.addRow('数据位：', self.sset_cb_data)

        # 校验位 下拉菜单
        self.sset_cb_parity = QComboBox(serial_setting_gb)
        self.sset_cb_parity.addItems(['N', 'E', 'O'])  # 校验位N－无校验，E－偶校验，O－奇校验
        # self.sset_cb_check.setCurrentIndex(0)
        serial_setting_formlayout.addRow('校验位：', self.sset_cb_parity)

        # 停止位 下拉菜单
        self.sset_cb_stop = QComboBox(serial_setting_gb)
        self.sset_cb_stop.addItems(['1', '1.5', '2'])
        # self.sset_cb_stop.setCurrentIndex(0)
        serial_setting_formlayout.addRow('停止位：', self.sset_cb_stop)

        # 窗口配色 下拉菜单
        self.sset_cb_color = QComboBox(serial_setting_gb)
        self.sset_cb_color.addItems(['whiteblack', 'blackwhite', 'blackgreen'])
        # self.sset_cb_color.setCurrentIndex(0)
        serial_setting_formlayout.addRow('窗口配色：', self.sset_cb_color)

        # 打开串口 按钮
        self.sset_btn_open = QPushButton('打开串口')
        self.sset_btn_open.setIcon(QIcon('open_button.png'))
        self.sset_btn_open.setEnabled(False)
        serial_setting_formlayout.addRow(self.sset_btn_open)

        serial_setting_formlayout.setSpacing(11)

        serial_setting_gb.setLayout(serial_setting_formlayout)
        return serial_setting_gb

    # 串口状态区
    def set_serial_state_groupbox(self):
        self.serial_state_gb = QGroupBox('Cable State', self)
        serial_state_formlayout = QFormLayout()

        # 已发送 标签
        self.sent_count_num = ""
        self.ssta_lb_sent = QLabel(str(self.sent_count_num))
        serial_state_formlayout.addRow('SRNM：', self.ssta_lb_sent)

        # 已接收 标签
        self.receive_count_num = ""
        self.ssta_lb_receive = QLabel(str(self.receive_count_num))
        serial_state_formlayout.addRow('iBoot：', self.ssta_lb_receive)

        # 版本标签
        self.versionstr = ""
        self.ssta_lb_version = QLabel(self.versionstr)
        serial_state_formlayout.addRow('ECID：', self.ssta_lb_version)
        self.ssta_lb_coder = QLabel('Author：Checker')
        serial_state_formlayout.addRow(self.ssta_lb_coder)

        serial_state_formlayout.setSpacing(13)
        self.serial_state_gb.setLayout(serial_state_formlayout)
        return self.serial_state_gb

    def showtime(self):
        pass
        # time_display = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss dddd')
        # self.ssta_lb_timer.setText(time_display)

    # 接收区
    def set_receive_groupbox(self):
        # 设置一个接收区分组框
        receive_gb = QGroupBox('接收区', self)
        # 添加显示接收日志的文本框
        self.receive_log_view = QTextBrowser(receive_gb)
        self.receive_log_view.setMinimumWidth(350)
        # self.receive_log_view.append('Hello，欢迎使用串口助手！\n')
        # 设置布局并添加文本框
        vbox = QVBoxLayout()
        vbox.addWidget(self.receive_log_view)
        # 设置接收区分组框的布局
        receive_gb.setLayout(vbox)
        # receive_gb.setFixedWidth(300)
        return receive_gb

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())