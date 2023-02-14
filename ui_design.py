import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QDesktopWidget, QGroupBox,
                             QGridLayout, QTextBrowser, QVBoxLayout, QFormLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox, QTextEdit,
                             QLineEdit, QHBoxLayout,QRadioButton)
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
        grid_layout.addWidget(self.set_account_groupbox(), 0, 0)
        grid_layout.addWidget(self.set_serial_setting_groupbox(), 1,0)
        grid_layout.addWidget(self.set_serial_state_groupbox(), 0, 1,2,1)
        # grid_layout.addWidget(self.set_receive_groupbox(), 0, 1)
        self.setLayout(grid_layout)
        self.resize(760, 420)
        self.setWindowIcon(QIcon('title_icon.png'))
        self.center()
        self.setWindowTitle('iPhone Checker')
        # self.setFixedSize(760, 450)
        self.show()
    def set_account_groupbox(self):
        account_gb = QGroupBox('账户')
        account_formlayout = QFormLayout()

        # 检测串口 按钮
        self.sset_btn_detect = QPushButton('登陆账号')
        self.sset_btn_detect.setFixedWidth(100)
        account_formlayout.addRow(self.sset_btn_detect)

        account_gb.setLayout(account_formlayout)
        account_formlayout.setSizeConstraint(12)
        return account_gb
    # 串口设置 区
    def set_serial_setting_groupbox(self):
        # 设置一个 串口设置 分组框
        serial_setting_gb = QGroupBox('设置')
        # 创建 串口设置 分组框内的布局管理器
        serial_setting_formlayout = QFormLayout()

        # 打开串口 按钮
        self.sset_btn_open = QPushButton('打开工程线')
        self.sset_btn_open.setIcon(QIcon('open_button.png'))
        self.sset_btn_open.setEnabled(False)
        self.sset_btn_open.setFixedWidth(100)
        serial_setting_formlayout.addRow(self.sset_btn_open)

        # self.sset_cb_items = QCheckBox("serial_setting_gb")
        self.checkBox1= QCheckBox("")
        self.checkBox1.setChecked(True)
        self.checkBox1.setFixedWidth(100)

        serial_setting_formlayout.addRow("激活锁查询（100积分）",self.checkBox1)

        self.checkBox2 = QCheckBox("")
        self.checkBox2.setChecked(True)
        self.checkBox2.setFixedWidth(100)

        serial_setting_formlayout.addRow("网络锁查询（100积分）",self.checkBox2)

        self.checkBox3 = QCheckBox("")
        self.checkBox3.setChecked(True)
        self.checkBox3.setFixedWidth(100)

        serial_setting_formlayout.addRow("运营商查询（100积分）",self.checkBox3)

        serial_setting_formlayout.setSpacing(13)

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

        # # 版本标签
        # self.versionstr = ""
        # self.ssta_lb_version = QLabel(self.versionstr)
        # serial_state_formlayout.addRow('ECID：', self.ssta_lb_version)
        # self.ssta_lb_coder = QLabel('Author：Checker')
        # serial_state_formlayout.addRow(self.ssta_lb_coder)

        serial_state_formlayout.setSpacing(5)
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
        self.receive_log_view.setMinimumWidth(600)
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