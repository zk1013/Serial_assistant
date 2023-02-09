import json
import os
import sys, re
import time
import configparser
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMessageBox, QFileDialog, QPushButton, QLineEdit, QCheckBox)
from PyQt5.QtGui import QColor, QIcon, QTextCursor
from PyQt5.QtCore import QTimer
from ui_design import SerialUi


class SerialAssistant(SerialUi):
    def __init__(self):
        super().__init__()
        # 初始化serial对象 用于串口通信
        self.ser = serial.Serial()
        # 初始化串口配置文件
        # self.serial_cfg()
        self.port_detect()
        # 初始化串口 绑定槽
        self.unit_serial()

    # 初始化串口配置 定义串口设置信息 保存和读取
    def serial_cfg(self):
        self.cfg_serial_dic = {'baudrate': '115200', 'data': '8', 'stopbits': '1', 'parity': 'N'}  # 用于保存串口设置信息的字典
        self.cfg_command_dic = {}
        self.cfg_single_dic = {}
        self.current_path = os.path.dirname(os.path.realpath(__file__))  # 当前目录
        self.cfg_path = ''  # 配置文件的路径
        self.cfg_dir = 'settings'  # 配置文件目录
        self.cfg_file_name = 'cfg.ini'  # 配置文件名
        self.conf_parse = configparser.ConfigParser()  # 配置文件解析ConfigParser对象

        # 读取串口配置
        self.read_cfg()
        # 将读取到的串口配置信息显示到界面上
        self.display_cfg()

    # 读取串口配置————配置文件和section是否存在
    def read_cfg(self):
        self.cfg_path = os.path.join(self.current_path, self.cfg_dir, self.cfg_file_name)  # 获取配置文件路径 join用于连接两个或更多的路径
        # 判断读取配置文件是否正常 如果读取文件正常
        if self.conf_parse.read(self.cfg_path):
            # 判断读取section是否正常
            try:
                # 获取serial_setting section  返回一个配置字典
                serial_items = self.conf_parse.items('serial_setting')
                self.cfg_serial_dic = dict(serial_items)
                print(self.cfg_serial_dic)
            # 如果没有找到section
            except configparser.NoSectionError:
                self.conf_parse.add_section('serial_setting')  # 添加section
                self.conf_parse.write(open(self.cfg_path, 'w'))  # 保存到配置文件
            try:
                command_items = self.conf_parse.items('mul_sent_command')
                self.cfg_command_dic = dict(command_items)
                print(self.cfg_command_dic)
            except configparser.NoSectionError:
                self.conf_parse.add_section('mul_sent_command')
                self.conf_parse.write(open(self.cfg_path, 'w'))
            try:
                command_items = self.conf_parse.items('single_sent_command')
                self.cfg_single_dic = dict(command_items)
                print(self.cfg_single_dic)
            except configparser.NoSectionError:
                self.conf_parse.add_section('single_sent_command')
                self.conf_parse.write(open(self.cfg_path, 'w'))
        # 读取文件异常
        else:
            # 判断setting目录是否存在 不存在的话新建目录
            if not os.path.exists(os.path.join(self.current_path, self.cfg_dir)):
                os.mkdir(os.path.join(self.current_path, self.cfg_dir))
            self.conf_parse.add_section('serial_setting')  # 添加section
            self.conf_parse.set('serial_setting', 'baudrate', '')
            self.conf_parse.set('serial_setting', 'data', '')
            self.conf_parse.set('serial_setting', 'stopbits', '')
            self.conf_parse.set('serial_setting', 'parity', '')
            self.conf_parse.add_section('mul_sent_command')
            for i in range(1, 8):
                self.conf_parse.set('mul_sent_command', 'command_{}'.format(i), '')
            self.conf_parse.add_section('single_sent_command')
            self.conf_parse.set('single_sent_command', 'command', '')
            self.conf_parse.write(open(self.cfg_path, 'w'))  # 保存到配置文件

    # 保存串口配置信息
    def save_cfg(self):
        self.conf_parse.set('serial_setting', 'baudrate', str(self.ser.baudrate))
        self.conf_parse.set('serial_setting', 'data', str(self.ser.bytesize))
        self.conf_parse.set('serial_setting', 'stopbits', str(self.ser.stopbits))
        self.conf_parse.set('serial_setting', 'parity', self.ser.parity)

        for i in range(1, 8):
            self.conf_parse.set('mul_sent_command', 'command_{}'.format(i),
                                self.findChild(QLineEdit, 'mul_le_{}'.format(i)).text())

        self.conf_parse.set('single_sent_command', 'command', self.sins_te_send.toPlainText())
        self.conf_parse.write(open(self.cfg_path, 'w'))

    # 将读取到的串口配置信息显示到界面上
    def display_cfg(self):
        self.sset_cb_baud.setCurrentText(self.conf_parse.get('serial_setting', 'baudrate'))
        self.sset_cb_data.setCurrentText(self.conf_parse.get('serial_setting', 'data'))
        self.sset_cb_stop.setCurrentText(self.conf_parse.get('serial_setting', 'stopbits'))
        self.sset_cb_parity.setCurrentText(self.conf_parse.get('serial_setting', 'parity'))

        for i in range(1, 8):
            command = self.conf_parse.get('mul_sent_command', 'command_{}'.format(i))
            if command:
                self.findChild(QLineEdit, 'mul_le_{}'.format(i)).setText(command)

        self.sins_te_send.setText(self.conf_parse.get('single_sent_command', 'command'))

    # 初始化串口 给各个信号绑定槽
    def unit_serial(self):
        # 串口检测按钮
        self.sset_btn_detect.clicked.connect(self.port_detect)
        # 打开/关闭串口 按钮
        self.sset_btn_open.clicked.connect(self.port_open_close)
        # 更改窗口颜色下拉菜单
        self.sset_cb_color.currentTextChanged.connect(self.change_color)
        # 单行发送数据 按钮
        # self.sins_btn_send.clicked.connect(self.single_send)
        # 清除接收按钮
        # self.muls_btn_clear.clicked.connect(self.clear_receive)
        # # 清除发送按钮
        # self.sins_btn_clear.clicked.connect(self.clear_send)
        # # 保存窗口
        # self.sins_btn_save.clicked.connect(self.save_receive_to_file)

        # 循环发送数据——单条
        # self.loop_single_send_timer = QTimer()
        # self.loop_single_send_timer.timeout.connect(self.single_send)
        # self.sins_cb_loop_send.stateChanged.connect(self.single_loop_send)

        # # 多行发送数据 按钮
        # for i in range(1, 8):
        #     self.child_button = self.findChild(QPushButton, 'mul_btn_{}'.format(i))
        #     self.child_button.clicked.connect(self.multi_send_general)
        #
        # # 循环发送数据——多条
        # self.loop_mul_sent_timer = QTimer()
        # self.loop_mul_sent_timer.timeout.connect(self.multi_send_special)
        # self.mul_cb_loop_send.stateChanged.connect(self.mul_loop_send)


    # 串口检测
    def port_detect(self):
        # 检测所有存在的串口 将信息存在字典中
        self.port_dict = {}
        self.com_name = ""
        port_list = list(serial.tools.list_ports.comports())
        for port in port_list:
            if "Kanzi" in  port[1]:
                self.port_dict["%s" % port[0]] = "%s" % port[1]
                self.com_name = port[0]
                self.port_open_close()
        if len(self.port_dict) == 0:
            self.serial_state_gb.setTitle('Cable State: Error')
        print(self.port_dict)

    # 获取端口号（串口选择界面想显示完全 但打开串口只需要串口号COMX）
    def get_port_name(self):
        full_name = self.sset_cb_choose.currentText()
        com_name = full_name[0:full_name.rfind('：')]
        print("com_name=",com_name)
        return com_name

    # 打开/关闭 串口
    def port_open_close(self):
        print("port_open_close")
        # 定时器接受数据
        self.serial_receive_timer = QTimer(self)
        self.serial_receive_timer.timeout.connect(self.data_receive)
        if self.port_dict:
            # {'baudrate': '115200', 'data': '8', 'stopbits': '1', 'parity': 'N'}
            self.ser.port = self.com_name  # 设置端口
            self.ser.baudrate = 115200  # 波特率
            self.ser.bytesize = 8  # 数据位
            self.ser.parity = "N"  # 校验位
            self.ser.stopbits = 1  # 停止位
            try:
                self.ser.open()
            except serial.SerialException:
                QMessageBox.critical(self, 'Open Port Error', '此数据线不能正常打开！')
                return None

            # 打开串口接收定时器 周期为2ms
            self.serial_receive_timer.start(2)

            if self.ser.isOpen():
                self.sset_btn_open.setText('关闭链接')
                self.sset_btn_open.setIcon(QIcon('close_button.png'))
                self.serial_state_gb.setTitle('Cable State: Connected')
                self.set_setting_enable(False)

# 改变窗口颜色
    def change_color(self):
        if self.sset_cb_color.currentText() == 'whiteblack':
            self.receive_log_view.setStyleSheet("QTextEdit {color:black;background-color:white}")
            # self.receive_log_view.setTextColor(QColor())
            # print('白底黑字')
        elif self.sset_cb_color.currentText() == 'blackwhite':
            self.receive_log_view.setStyleSheet("QTextEdit {color:white;background-color:black}")
            # print('黑底白字')
        elif self.sset_cb_color.currentText() == 'blackgreen':
            self.receive_log_view.setStyleSheet("QTextEdit {color:rgb(0,255,0);background-color:black}")
            self.receive_log_view.setTextColor(QColor('red'))
            # print('黑底绿字')
    def getDeviceinfos(self):
        infojson = '''[{"name":"iPhone 2G","identifier":"iPhone1,1","boards":[{"boardconfig":"m68ap","platform":"s5l8900x","cpid":35072,"bdid":0}],"boardconfig":"m68ap","platform":"s5l8900x","cpid":35072,"bdid":0},{"name":"iPhone 3G","identifier":"iPhone1,2","boards":[{"boardconfig":"n82ap","platform":"s5l8900x","cpid":35072,"bdid":4}],"boardconfig":"n82ap","platform":"s5l8900x","cpid":35072,"bdid":4},{"name":"iPhone 3G[S]","identifier":"iPhone2,1","boards":[{"boardconfig":"n88ap","platform":"s5l8920x","cpid":35104,"bdid":0}],"boardconfig":"n88ap","platform":"s5l8920x","cpid":35104,"bdid":0},{"name":"iPhone 4 (GSM)","identifier":"iPhone3,1","boards":[{"boardconfig":"n90ap","platform":"s5l8930x","cpid":35120,"bdid":0}],"boardconfig":"n90ap","platform":"s5l8930x","cpid":35120,"bdid":0},{"name":"iPhone 4 (CDMA)","identifier":"iPhone3,3","boards":[{"boardconfig":"n92ap","platform":"s5l8930x","cpid":35120,"bdid":6}],"boardconfig":"n92ap","platform":"s5l8930x","cpid":35120,"bdid":6},{"name":"iPhone 4[S]","identifier":"iPhone4,1","boards":[{"boardconfig":"n94ap","platform":"s5l8940x","cpid":35136,"bdid":8}],"boardconfig":"n94ap","platform":"s5l8940x","cpid":35136,"bdid":8},{"name":"iPod touch 1G","identifier":"iPod1,1","boards":[{"boardconfig":"n45ap","platform":"s5l8900x","cpid":35072,"bdid":2}],"boardconfig":"n45ap","platform":"s5l8900x","cpid":35072,"bdid":2},{"name":"iPod touch 2G","identifier":"iPod2,1","boards":[{"boardconfig":"n72ap","platform":"s5l8720x","cpid":34592,"bdid":0}],"boardconfig":"n72ap","platform":"s5l8720x","cpid":34592,"bdid":0},{"name":"iPod touch 3","identifier":"iPod3,1","boards":[{"boardconfig":"n18ap","platform":"s5l8922x","cpid":35106,"bdid":2}],"boardconfig":"n18ap","platform":"s5l8922x","cpid":35106,"bdid":2},{"name":"iPod touch 4","identifier":"iPod4,1","boards":[{"boardconfig":"n81ap","platform":"s5l8930x","cpid":35120,"bdid":8}],"boardconfig":"n81ap","platform":"s5l8930x","cpid":35120,"bdid":8},{"name":"iPad 1","identifier":"iPad1,1","boards":[{"boardconfig":"k48ap","platform":"s5l8930x","cpid":35120,"bdid":2}],"boardconfig":"k48ap","platform":"s5l8930x","cpid":35120,"bdid":2},{"name":"iPad 2 (WiFi)","identifier":"iPad2,1","boards":[{"boardconfig":"k93ap","platform":"s5l8940x","cpid":35136,"bdid":4}],"boardconfig":"k93ap","platform":"s5l8940x","cpid":35136,"bdid":4},{"name":"iPad 2 (GSM)","identifier":"iPad2,2","boards":[{"boardconfig":"k94ap","platform":"s5l8940x","cpid":35136,"bdid":6}],"boardconfig":"k94ap","platform":"s5l8940x","cpid":35136,"bdid":6},{"name":"iPad 2 (CDMA)","identifier":"iPad2,3","boards":[{"boardconfig":"k95ap","platform":"s5l8940x","cpid":35136,"bdid":2}],"boardconfig":"k95ap","platform":"s5l8940x","cpid":35136,"bdid":2},{"name":"iPad 2 (Mid 2012)","identifier":"iPad2,4","boards":[{"boardconfig":"k93aap","platform":"s5l8942x","cpid":35138,"bdid":6}],"boardconfig":"k93aap","platform":"s5l8942x","cpid":35138,"bdid":6},{"name":"iPad 3 (WiFi)","identifier":"iPad3,1","boards":[{"boardconfig":"j1ap","platform":"s5l8945x","cpid":35141,"bdid":0}],"boardconfig":"j1ap","platform":"s5l8945x","cpid":35141,"bdid":0},{"name":"iPad 3 (CDMA)","identifier":"iPad3,2","boards":[{"boardconfig":"j2ap","platform":"s5l8945x","cpid":35141,"bdid":2}],"boardconfig":"j2ap","platform":"s5l8945x","cpid":35141,"bdid":2},{"name":"iPad 3 (GSM)","identifier":"iPad3,3","boards":[{"boardconfig":"j2aap","platform":"s5l8945x","cpid":35141,"bdid":4}],"boardconfig":"j2aap","platform":"s5l8945x","cpid":35141,"bdid":4},{"name":"Apple TV 2G","identifier":"AppleTV2,1","boards":[{"boardconfig":"k66ap","platform":"s5l8930x","cpid":35120,"bdid":16}],"boardconfig":"k66ap","platform":"s5l8930x","cpid":35120,"bdid":16},{"name":"Apple TV 3","identifier":"AppleTV3,1","boards":[{"boardconfig":"J33AP","platform":"s5l8942x","cpid":35138,"bdid":8}],"boardconfig":"J33AP","platform":"s5l8942x","cpid":35138,"bdid":8},{"name":"iPod touch 5","identifier":"iPod5,1","boards":[{"boardconfig":"n78ap","platform":"s5l8942x","cpid":35138,"bdid":0}],"boardconfig":"n78ap","platform":"s5l8942x","cpid":35138,"bdid":0},{"name":"iPhone 4 (GSM / 2012)","identifier":"iPhone3,2","boards":[{"boardconfig":"n90bap","platform":"s5l8930x","cpid":35120,"bdid":4}],"boardconfig":"n90bap","platform":"s5l8930x","cpid":35120,"bdid":4},{"name":"iPhone 5 (GSM)","identifier":"iPhone5,1","boards":[{"boardconfig":"N41AP","platform":"s5l8950x","cpid":35152,"bdid":0}],"boardconfig":"N41AP","platform":"s5l8950x","cpid":35152,"bdid":0},{"name":"iPhone 5 (Global)","identifier":"iPhone5,2","boards":[{"boardconfig":"N42AP","platform":"s5l8950x","cpid":35152,"bdid":2}],"boardconfig":"N42AP","platform":"s5l8950x","cpid":35152,"bdid":2},{"name":"iPad Mini (WiFi)","identifier":"iPad2,5","boards":[{"boardconfig":"p105ap","platform":"s5l8942x","cpid":35138,"bdid":10}],"boardconfig":"p105ap","platform":"s5l8942x","cpid":35138,"bdid":10},{"name":"iPad Mini (GSM)","identifier":"iPad2,6","boards":[{"boardconfig":"p106ap","platform":"s5l8942x","cpid":35138,"bdid":12}],"boardconfig":"p106ap","platform":"s5l8942x","cpid":35138,"bdid":12},{"name":"iPad Mini (Global)","identifier":"iPad2,7","boards":[{"boardconfig":"p107ap","platform":"s5l8942x","cpid":35138,"bdid":14}],"boardconfig":"p107ap","platform":"s5l8942x","cpid":35138,"bdid":14},{"name":"iPad 4 (WiFi)","identifier":"iPad3,4","boards":[{"boardconfig":"P101AP","platform":"s5l8955x","cpid":35157,"bdid":0}],"boardconfig":"P101AP","platform":"s5l8955x","cpid":35157,"bdid":0},{"name":"iPad 4 (GSM)","identifier":"iPad3,5","boards":[{"boardconfig":"P102AP","platform":"s5l8955x","cpid":35157,"bdid":2}],"boardconfig":"P102AP","platform":"s5l8955x","cpid":35157,"bdid":2},{"name":"iPad 4 (Global)","identifier":"iPad3,6","boards":[{"boardconfig":"P103AP","platform":"s5l8955x","cpid":35157,"bdid":4}],"boardconfig":"P103AP","platform":"s5l8955x","cpid":35157,"bdid":4},{"name":"iPhone 5s (Global)","identifier":"iPhone6,2","boards":[{"boardconfig":"N53AP","platform":"s5l8960x","cpid":35168,"bdid":2}],"boardconfig":"N53AP","platform":"s5l8960x","cpid":35168,"bdid":2},{"name":"iPhone 5c (GSM)","identifier":"iPhone5,3","boards":[{"boardconfig":"N48AP","platform":"s5l8950x","cpid":35152,"bdid":10}],"boardconfig":"N48AP","platform":"s5l8950x","cpid":35152,"bdid":10},{"name":"iPhone 5c (Global)","identifier":"iPhone5,4","boards":[{"boardconfig":"N49AP","platform":"s5l8950x","cpid":35152,"bdid":14}],"boardconfig":"N49AP","platform":"s5l8950x","cpid":35152,"bdid":14},{"name":"iPhone 5s (GSM)","identifier":"iPhone6,1","boards":[{"boardconfig":"N51AP","platform":"s5l8960x","cpid":35168,"bdid":0}],"boardconfig":"N51AP","platform":"s5l8960x","cpid":35168,"bdid":0},{"name":"iPad Mini 2 (WiFi)","identifier":"iPad4,4","boards":[{"boardconfig":"J85AP","platform":"s5l8960x","cpid":35168,"bdid":10}],"boardconfig":"J85AP","platform":"s5l8960x","cpid":35168,"bdid":10},{"name":"iPad Mini 2 (Cellular)","identifier":"iPad4,5","boards":[{"boardconfig":"J86AP","platform":"s5l8960x","cpid":35168,"bdid":12}],"boardconfig":"J86AP","platform":"s5l8960x","cpid":35168,"bdid":12},{"name":"iPad Air (WiFi)","identifier":"iPad4,1","boards":[{"boardconfig":"J71AP","platform":"s5l8960x","cpid":35168,"bdid":16}],"boardconfig":"J71AP","platform":"s5l8960x","cpid":35168,"bdid":16},{"name":"iPad Air (Cellular)","identifier":"iPad4,2","boards":[{"boardconfig":"J72AP","platform":"s5l8960x","cpid":35168,"bdid":18}],"boardconfig":"J72AP","platform":"s5l8960x","cpid":35168,"bdid":18},{"name":"iPad Air (China)","identifier":"iPad4,3","boards":[{"boardconfig":"J73AP","platform":"s5l8960x","cpid":35168,"bdid":20}],"boardconfig":"J73AP","platform":"s5l8960x","cpid":35168,"bdid":20},{"name":"iPad Mini 2 (China)","identifier":"iPad4,6","boards":[{"boardconfig":"J87AP","platform":"s5l8960x","cpid":35168,"bdid":14}],"boardconfig":"J87AP","platform":"s5l8960x","cpid":35168,"bdid":14},{"name":"iPhone 6+","identifier":"iPhone7,1","boards":[{"boardconfig":"N56AP","platform":"t7000","cpid":28672,"bdid":4}],"boardconfig":"N56AP","platform":"t7000","cpid":28672,"bdid":4},{"name":"iPhone 6","identifier":"iPhone7,2","boards":[{"boardconfig":"N61AP","platform":"t7000","cpid":28672,"bdid":6}],"boardconfig":"N61AP","platform":"t7000","cpid":28672,"bdid":6},{"name":"iPad Mini 3 (WiFi)","identifier":"iPad4,7","boards":[{"boardconfig":"J85mAP","platform":"s5l8960x","cpid":35168,"bdid":50}],"boardconfig":"J85mAP","platform":"s5l8960x","cpid":35168,"bdid":50},{"name":"iPad Mini 3 (Cellular)","identifier":"iPad4,8","boards":[{"boardconfig":"J86mAP","platform":"s5l8960x","cpid":35168,"bdid":52}],"boardconfig":"J86mAP","platform":"s5l8960x","cpid":35168,"bdid":52},{"name":"iPad Mini 3 (China)","identifier":"iPad4,9","boards":[{"boardconfig":"J87mAP","platform":"s5l8960x","cpid":35168,"bdid":54}],"boardconfig":"J87mAP","platform":"s5l8960x","cpid":35168,"bdid":54},{"name":"iPad Air 2 (WiFi)","identifier":"iPad5,3","boards":[{"boardconfig":"J81AP","platform":"t7001","cpid":28673,"bdid":6}],"boardconfig":"J81AP","platform":"t7001","cpid":28673,"bdid":6},{"name":"iPad Air 2 (Cellular)","identifier":"iPad5,4","boards":[{"boardconfig":"J82AP","platform":"t7001","cpid":28673,"bdid":2}],"boardconfig":"J82AP","platform":"t7001","cpid":28673,"bdid":2},{"name":"iPod touch 6","identifier":"iPod7,1","boards":[{"boardconfig":"N102AP","platform":"t7000","cpid":28672,"bdid":16}],"boardconfig":"N102AP","platform":"t7000","cpid":28672,"bdid":16},{"name":"iPad Mini 4 (WiFi)","identifier":"iPad5,1","boards":[{"boardconfig":"J96AP","platform":"t7000","cpid":28672,"bdid":8}],"boardconfig":"J96AP","platform":"t7000","cpid":28672,"bdid":8},{"name":"iPad Mini 4 (Cellular)","identifier":"iPad5,2","boards":[{"boardconfig":"J97AP","platform":"t7000","cpid":28672,"bdid":10}],"boardconfig":"J97AP","platform":"t7000","cpid":28672,"bdid":10},{"name":"iPhone 6s","identifier":"iPhone8,1","boards":[{"boardconfig":"N71AP","platform":"s8000","cpid":32768,"bdid":4},{"boardconfig":"N71mAP","platform":"s8003","cpid":32771,"bdid":4}],"boardconfig":"N71AP","platform":"s8000","cpid":32768,"bdid":4},{"name":"Apple TV 4 (2015)","identifier":"AppleTV5,3","boards":[{"boardconfig":"J42dAP","platform":"t7000","cpid":28672,"bdid":52}],"boardconfig":"J42dAP","platform":"t7000","cpid":28672,"bdid":52},{"name":"iPhone 8 (Global)","identifier":"iPhone10,1","boards":[{"boardconfig":"D20AP","platform":"t8015","cpid":32789,"bdid":2}],"boardconfig":"D20AP","platform":"t8015","cpid":32789,"bdid":2},{"name":"iPhone 8 (GSM)","identifier":"iPhone10,4","boards":[{"boardconfig":"D201AP","platform":"t8015","cpid":32789,"bdid":10}],"boardconfig":"D201AP","platform":"t8015","cpid":32789,"bdid":10},{"name":"iPhone 8 Plus (GSM)","identifier":"iPhone10,5","boards":[{"boardconfig":"D211AP","platform":"t8015","cpid":32789,"bdid":12}],"boardconfig":"D211AP","platform":"t8015","cpid":32789,"bdid":12},{"name":"iPhone 8 Plus (Global)","identifier":"iPhone10,2","boards":[{"boardconfig":"D21AP","platform":"t8015","cpid":32789,"bdid":4}],"boardconfig":"D21AP","platform":"t8015","cpid":32789,"bdid":4},{"name":"iPhone X (Global)","identifier":"iPhone10,3","boards":[{"boardconfig":"D22AP","platform":"t8015","cpid":32789,"bdid":6}],"boardconfig":"D22AP","platform":"t8015","cpid":32789,"bdid":6},{"name":"iPhone X (GSM)","identifier":"iPhone10,6","boards":[{"boardconfig":"D221AP","platform":"t8015","cpid":32789,"bdid":14}],"boardconfig":"D221AP","platform":"t8015","cpid":32789,"bdid":14},{"name":"iPhone XS Max","identifier":"iPhone11,6","boards":[{"boardconfig":"D331pAP","platform":"t8020","cpid":32800,"bdid":26}],"boardconfig":"D331pAP","platform":"t8020","cpid":32800,"bdid":26},{"name":"iPhone XS","identifier":"iPhone11,2","boards":[{"boardconfig":"D321AP","platform":"t8020","cpid":32800,"bdid":14}],"boardconfig":"D321AP","platform":"t8020","cpid":32800,"bdid":14},{"name":"iPhone XS Max (China)","identifier":"iPhone11,4","boards":[{"boardconfig":"D331AP","platform":"t8020","cpid":32800,"bdid":10}],"boardconfig":"D331AP","platform":"t8020","cpid":32800,"bdid":10},{"name":"iPhone XR","identifier":"iPhone11,8","boards":[{"boardconfig":"N841AP","platform":"t8020","cpid":32800,"bdid":12}],"boardconfig":"N841AP","platform":"t8020","cpid":32800,"bdid":12},{"name":"iPad Mini 5 (WiFi)","identifier":"iPad11,1","boards":[{"boardconfig":"J210AP","platform":"t8020","cpid":32800,"bdid":20}],"boardconfig":"J210AP","platform":"t8020","cpid":32800,"bdid":20},{"name":"iPad Mini 5 (Cellular)","identifier":"iPad11,2","boards":[{"boardconfig":"J211AP","platform":"t8020","cpid":32800,"bdid":22}],"boardconfig":"J211AP","platform":"t8020","cpid":32800,"bdid":22},{"name":"iPad Air 3 (WiFi)","identifier":"iPad11,3","boards":[{"boardconfig":"J217AP","platform":"t8020","cpid":32800,"bdid":28}],"boardconfig":"J217AP","platform":"t8020","cpid":32800,"bdid":28},{"name":"iPad Air 3 (Cellular)","identifier":"iPad11,4","boards":[{"boardconfig":"J218AP","platform":"t8020","cpid":32800,"bdid":30}],"boardconfig":"J218AP","platform":"t8020","cpid":32800,"bdid":30}]'''
        d = json.loads(infojson)
        for l in d:
            if len(l['boards']) > 1:
                print(l)

    # 设置 串口设置区 可用与禁用
    def set_setting_enable(self, enable):
        self.sset_cb_choose.setEnabled(enable)
        self.sset_cb_baud.setEnabled(enable)
        self.sset_cb_data.setEnabled(enable)
        self.sset_cb_parity.setEnabled(enable)
        self.sset_cb_stop.setEnabled(enable)

    # 接收数据
    def data_receive(self):
        try:
            # inWaiting()：返回接收缓存中的字节数
            num = self.ser.inWaiting()
        except:
            pass
        else:
            if num > 0:
                data = self.ser.read(num)
                receive_num = len(data)

                receive_string = data.decode(encoding='gbk', errors='replace')
                # print(receive_string)
                self.receive_log_view.insertPlainText(receive_string)
                self.receive_log_view.moveCursor(QTextCursor.End)
                # if len(re.findall(r'Delay', receive_string)) > 0 or \
                #         len(re.findall(r'seconds', receive_string)) > 0 or \
                #         len(re.findall(r'enter', receive_string)) > 0:
                #     print(self.receive_log_view.toPlainText())
                #     self.receive_log_view.setText('')

                findstr = self.receive_log_view.toPlainText()
                self.ecid = ""
                res = re.findall(r'iBoot-(\d+\.\d+\.\d+)', findstr)
                if len(res) > 0:
                    # print(receive_string)
                    iboot = res[0]
                    print("iboot",iboot)
                    self.receive_count_num = iboot
                    self.ssta_lb_receive.setText(str(self.receive_count_num))
                res = re.findall(r'CPID:(\d+)', findstr)
                if len(res) > 0:
                    # print(receive_string)
                    cpid = res[0]
                    print("cpid",cpid)
                res = re.findall(r'ECID:([a-zA-Z0-9]+)', findstr)
                if len(res) > 0:
                    # print(receive_string)
                    self.ecid = res[0]
                    print("ecid",self.ecid)
                    self.ssta_lb_version.setText(str(self.ecid))
                res = re.findall(r"([a-zA-Z0-9]{12})\]", findstr)
                if len(res) > 0:
                    # print(receive_string)
                    snrm = res[0]
                    print("snrm",snrm)
                    self.sent_count_num = snrm
                    self.ssta_lb_sent.setText(str(self.sent_count_num))
                    print(findstr)
                    self.receive_log_view.setText('')
                res = re.findall(r"\(([a-zA-Z0-9]+)\)", findstr)
                if len(res) > 0:
                    boardid = res[0]
                    print("Board",boardid)
                    self.ssta_lb_coder.setText(boardid)
                    print(self.getboardinfo(boardid))
            else:
                pass
    def getboardinfo(self,boardid):
        infodict = {'D74AP': {'name': 'iPhone 14 Pro Max', 'identifier': 'iPhone15,3', 'BoardConfig': 'D74AP', 'Platform': 't8120', 'BDID': '0xE', 'CPID': '0x8120'}, 'D73AP': {'name': 'iPhone 14 Pro', 'identifier': 'iPhone15,2', 'BoardConfig': 'D73AP', 'Platform': 't8120', 'BDID': '0xC', 'CPID': '0x8120'}, 'D28AP': {'name': 'iPhone 14 Plus', 'identifier': 'iPhone14,8', 'BoardConfig': 'D28AP', 'Platform': 't8110', 'BDID': '0x1A', 'CPID': '0x8110'}, 'D27AP': {'name': 'iPhone 14', 'identifier': 'iPhone14,7', 'BoardConfig': 'D27AP', 'Platform': 't8110', 'BDID': '0x18', 'CPID': '0x8110'}, 'D49AP': {'name': 'iPhone SE (3rd generation)', 'identifier': 'iPhone14,6', 'BoardConfig': 'D49AP', 'Platform': 't8110', 'BDID': '0x10', 'CPID': '0x8110'}, 'D17AP': {'name': 'iPhone 13', 'identifier': 'iPhone14,5', 'BoardConfig': 'D17AP', 'Platform': 't8110', 'BDID': '0xA', 'CPID': '0x8110'}, 'D16AP': {'name': 'iPhone 13 mini', 'identifier': 'iPhone14,4', 'BoardConfig': 'D16AP', 'Platform': 't8110', 'BDID': '0x8', 'CPID': '0x8110'}, 'D64AP': {'name': 'iPhone 13 Pro Max', 'identifier': 'iPhone14,3', 'BoardConfig': 'D64AP', 'Platform': 't8110', 'BDID': '0xE', 'CPID': '0x8110'}, 'D63AP': {'name': 'iPhone 13 Pro', 'identifier': 'iPhone14,2', 'BoardConfig': 'D63AP', 'Platform': 't8110', 'BDID': '0xC', 'CPID': '0x8110'}, 'D17DEV': {'name': 'iPhone 13', 'identifier': 'iPhone14,5', 'BoardConfig': 'D17DEV', 'Platform': 't8110', 'BDID': '0xB', 'CPID': '0x8110'}, 'D16DEV': {'name': 'iPhone 13 mini', 'identifier': 'iPhone14,4', 'BoardConfig': 'D16DEV', 'Platform': 't8110', 'BDID': '0x9', 'CPID': '0x8110'}, 'D64DEV': {'name': 'iPhone 13 Pro Max', 'identifier': 'iPhone14,3', 'BoardConfig': 'D64DEV', 'Platform': 't8110', 'BDID': '0xF', 'CPID': '0x8110'}, 'D63DEV': {'name': 'iPhone 13 Pro', 'identifier': 'iPhone14,2', 'BoardConfig': 'D63DEV', 'Platform': 't8110', 'BDID': '0xD', 'CPID': '0x8110'}, 'D53PAP': {'name': 'iPhone 12 Pro', 'identifier': 'iPhone13,3', 'BoardConfig': 'D53pAP', 'Platform': 't8101', 'BDID': '0xE', 'CPID': '0x8101'}, 'D54PAP': {'name': 'iPhone 12 Pro Max', 'identifier': 'iPhone13,4', 'BoardConfig': 'D54pAP', 'Platform': 't8101', 'BDID': '0x8', 'CPID': '0x8101'}, 'D52GAP': {'name': 'iPhone 12 mini', 'identifier': 'iPhone13,1', 'BoardConfig': 'D52gAP', 'Platform': 't8101', 'BDID': '0xA', 'CPID': '0x8101'}, 'D53GAP': {'name': 'iPhone 12', 'identifier': 'iPhone13,2', 'BoardConfig': 'D53gAP', 'Platform': 't8101', 'BDID': '0xC', 'CPID': '0x8101'}, 'D79AP': {'name': 'iPhone SE (2020)', 'identifier': 'iPhone12,8', 'BoardConfig': 'D79AP', 'Platform': 't8030', 'BDID': '0x10', 'CPID': '0x8030'}, 'D421AP': {'name': 'iPhone 11 Pro', 'identifier': 'iPhone12,3', 'BoardConfig': 'D421AP', 'Platform': 't8030', 'BDID': '0x6', 'CPID': '0x8030'}, 'N104AP': {'name': 'iPhone 11', 'identifier': 'iPhone12,1', 'BoardConfig': 'N104AP', 'Platform': 't8030', 'BDID': '0x4', 'CPID': '0x8030'}, 'D431AP': {'name': 'iPhone 11 Pro Max', 'identifier': 'iPhone12,5', 'BoardConfig': 'D431AP', 'Platform': 't8030', 'BDID': '0x2', 'CPID': '0x8030'}, 'N841AP': {'name': 'iPhone XR', 'identifier': 'iPhone11,8', 'BoardConfig': 'N841AP', 'Platform': 't8020', 'BDID': '0xC', 'CPID': '0x8020'}, 'D331AP': {'name': 'iPhone XS Max (China)', 'identifier': 'iPhone11,4', 'BoardConfig': 'D331AP', 'Platform': 't8020', 'BDID': '0xA', 'CPID': '0x8020'}, 'D321AP': {'name': 'iPhone XS', 'identifier': 'iPhone11,2', 'BoardConfig': 'D321AP', 'Platform': 't8020', 'BDID': '0xE', 'CPID': '0x8020'}, 'D331PAP': {'name': 'iPhone XS Max', 'identifier': 'iPhone11,6', 'BoardConfig': 'D331pAP', 'Platform': 't8020', 'BDID': '0x1A', 'CPID': '0x8020'}, 'D221AP': {'name': 'iPhone X (GSM)', 'identifier': 'iPhone10,6', 'BoardConfig': 'D221AP', 'Platform': 't8015', 'BDID': '0xE', 'CPID': '0x8015'}, 'D22AP': {'name': 'iPhone X (Global)', 'identifier': 'iPhone10,3', 'BoardConfig': 'D22AP', 'Platform': 't8015', 'BDID': '0x6', 'CPID': '0x8015'}, 'D21AP': {'name': 'iPhone 8 Plus (Global)', 'identifier': 'iPhone10,2', 'BoardConfig': 'D21AP', 'Platform': 't8015', 'BDID': '0x4', 'CPID': '0x8015'}, 'D211AP': {'name': 'iPhone 8 Plus (GSM)', 'identifier': 'iPhone10,5', 'BoardConfig': 'D211AP', 'Platform': 't8015', 'BDID': '0xC', 'CPID': '0x8015'}, 'D201AP': {'name': 'iPhone 8 (GSM)', 'identifier': 'iPhone10,4', 'BoardConfig': 'D201AP', 'Platform': 't8015', 'BDID': '0xA', 'CPID': '0x8015'}, 'D20AP': {'name': 'iPhone 8 (Global)', 'identifier': 'iPhone10,1', 'BoardConfig': 'D20AP', 'Platform': 't8015', 'BDID': '0x2', 'CPID': '0x8015'}, 'D111AP': {'name': 'iPhone 7 Plus (GSM)', 'identifier': 'iPhone9,4', 'BoardConfig': 'D111AP', 'Platform': 't8010', 'BDID': '0xE', 'CPID': '0x8010'}, 'D101AP': {'name': 'iPhone 7 (GSM)', 'identifier': 'iPhone9,3', 'BoardConfig': 'D101AP', 'Platform': 't8010', 'BDID': '0xC', 'CPID': '0x8010'}, 'D11AP': {'name': 'iPhone 7 Plus (Global)', 'identifier': 'iPhone9,2', 'BoardConfig': 'D11AP', 'Platform': 't8010', 'BDID': '0xA', 'CPID': '0x8010'}, 'D10AP': {'name': 'iPhone 7 (Global)', 'identifier': 'iPhone9,1', 'BoardConfig': 'D10AP', 'Platform': 't8010', 'BDID': '0x8', 'CPID': '0x8010'}, 'N69AP': {'name': 'iPhone SE', 'identifier': 'iPhone8,4', 'BoardConfig': 'N69AP', 'Platform': 's8003', 'BDID': '0x2', 'CPID': '0x8003'}, 'N66AP': {'name': 'iPhone 6s+', 'identifier': 'iPhone8,2', 'BoardConfig': 'N66AP', 'Platform': 's8000', 'BDID': '0x6', 'CPID': '0x8000'}, 'N71AP': {'name': 'iPhone 6s', 'identifier': 'iPhone8,1', 'BoardConfig': 'N71AP', 'Platform': 's8000', 'BDID': '0x4', 'CPID': '0x8000'}, 'N69UAP': {'name': 'iPhone SE', 'identifier': 'iPhone8,4', 'BoardConfig': 'N69uAP', 'Platform': 's8000', 'BDID': '0x2', 'CPID': '0x8000'}, 'N66MAP': {'name': 'iPhone 6s+', 'identifier': 'iPhone8,2', 'BoardConfig': 'N66mAP', 'Platform': 's8003', 'BDID': '0x6', 'CPID': '0x8003'}, 'N71MAP': {'name': 'iPhone 6s', 'identifier': 'iPhone8,1', 'BoardConfig': 'N71mAP', 'Platform': 's8003', 'BDID': '0x4', 'CPID': '0x8003'}, 'N61AP': {'name': 'iPhone 6', 'identifier': 'iPhone7,2', 'BoardConfig': 'N61AP', 'Platform': 't7000', 'BDID': '0x6', 'CPID': '0x7000'}, 'N56AP': {'name': 'iPhone 6+', 'identifier': 'iPhone7,1', 'BoardConfig': 'N56AP', 'Platform': 't7000', 'BDID': '0x4', 'CPID': '0x7000'}, 'N51AP': {'name': 'iPhone 5s (GSM)', 'identifier': 'iPhone6,1', 'BoardConfig': 'N51AP', 'Platform': 's5l8960x', 'BDID': '0x0', 'CPID': '0x8960'}, 'N49AP': {'name': 'iPhone 5c (Global)', 'identifier': 'iPhone5,4', 'BoardConfig': 'N49AP', 'Platform': 's5l8950x', 'BDID': '0xE', 'CPID': '0x8950'}, 'N48AP': {'name': 'iPhone 5c (GSM)', 'identifier': 'iPhone5,3', 'BoardConfig': 'N48AP', 'Platform': 's5l8950x', 'BDID': '0xA', 'CPID': '0x8950'}, 'N53AP': {'name': 'iPhone 5s (Global)', 'identifier': 'iPhone6,2', 'BoardConfig': 'N53AP', 'Platform': 's5l8960x', 'BDID': '0x2', 'CPID': '0x8960'}, 'N42AP': {'name': 'iPhone 5 (Global)', 'identifier': 'iPhone5,2', 'BoardConfig': 'N42AP', 'Platform': 's5l8950x', 'BDID': '0x2', 'CPID': '0x8950'}, 'N41AP': {'name': 'iPhone 5 (GSM)', 'identifier': 'iPhone5,1', 'BoardConfig': 'N41AP', 'Platform': 's5l8950x', 'BDID': '0x0', 'CPID': '0x8950'}, 'N90BAP': {'name': 'iPhone 4 (GSM / 2012)', 'identifier': 'iPhone3,2', 'BoardConfig': 'n90bap', 'Platform': 's5l8930x', 'BDID': '0x4', 'CPID': '0x8930'}, 'N94AP': {'name': 'iPhone 4[S]', 'identifier': 'iPhone4,1', 'BoardConfig': 'n94ap', 'Platform': 's5l8940x', 'BDID': '0x8', 'CPID': '0x8940'}, 'N92AP': {'name': 'iPhone 4 (CDMA)', 'identifier': 'iPhone3,3', 'BoardConfig': 'n92ap', 'Platform': 's5l8930x', 'BDID': '0x6', 'CPID': '0x8930'}, 'N90AP': {'name': 'iPhone 4 (GSM)', 'identifier': 'iPhone3,1', 'BoardConfig': 'n90ap', 'Platform': 's5l8930x', 'BDID': '0x0', 'CPID': '0x8930'}, 'N88AP': {'name': 'iPhone 3G[S]', 'identifier': 'iPhone2,1', 'BoardConfig': 'n88ap', 'Platform': 's5l8920x', 'BDID': '0x0', 'CPID': '0x8920'}, 'N82AP': {'name': 'iPhone 3G', 'identifier': 'iPhone1,2', 'BoardConfig': 'n82ap', 'Platform': 's5l8900x', 'BDID': '0x4', 'CPID': '0x8900'}, 'M68AP': {'name': 'iPhone 2G', 'identifier': 'iPhone1,1', 'BoardConfig': 'm68ap', 'Platform': 's5l8900x', 'BDID': '0x0', 'CPID': '0x8900'}}
        res = infodict[boardid.upper()]
        return res
    def getbootversion(self,v1,v2,v3):
        # SELECT * FROM `fa_iosiboot` WHERE locate('7429.12.14',v1) and locate('beta',b1) = 0
        if v1 in (3460):
            pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "确定要退出吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
        if reply == QMessageBox.Yes:
            # self.save_cfg()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    su = SerialAssistant()
    sys.exit(app.exec_())

# infojson = '''[{"name":"iPhone 2G","identifier":"iPhone1,1","boards":[{"boardconfig":"m68ap","platform":"s5l8900x","cpid":35072,"bdid":0}],"boardconfig":"m68ap","platform":"s5l8900x","cpid":35072,"bdid":0},{"name":"iPhone 3G","identifier":"iPhone1,2","boards":[{"boardconfig":"n82ap","platform":"s5l8900x","cpid":35072,"bdid":4}],"boardconfig":"n82ap","platform":"s5l8900x","cpid":35072,"bdid":4},{"name":"iPhone 3G[S]","identifier":"iPhone2,1","boards":[{"boardconfig":"n88ap","platform":"s5l8920x","cpid":35104,"bdid":0}],"boardconfig":"n88ap","platform":"s5l8920x","cpid":35104,"bdid":0},{"name":"iPhone 4 (GSM)","identifier":"iPhone3,1","boards":[{"boardconfig":"n90ap","platform":"s5l8930x","cpid":35120,"bdid":0}],"boardconfig":"n90ap","platform":"s5l8930x","cpid":35120,"bdid":0},{"name":"iPhone 4 (CDMA)","identifier":"iPhone3,3","boards":[{"boardconfig":"n92ap","platform":"s5l8930x","cpid":35120,"bdid":6}],"boardconfig":"n92ap","platform":"s5l8930x","cpid":35120,"bdid":6},{"name":"iPhone 4[S]","identifier":"iPhone4,1","boards":[{"boardconfig":"n94ap","platform":"s5l8940x","cpid":35136,"bdid":8}],"boardconfig":"n94ap","platform":"s5l8940x","cpid":35136,"bdid":8},{"name":"iPod touch 1G","identifier":"iPod1,1","boards":[{"boardconfig":"n45ap","platform":"s5l8900x","cpid":35072,"bdid":2}],"boardconfig":"n45ap","platform":"s5l8900x","cpid":35072,"bdid":2},{"name":"iPod touch 2G","identifier":"iPod2,1","boards":[{"boardconfig":"n72ap","platform":"s5l8720x","cpid":34592,"bdid":0}],"boardconfig":"n72ap","platform":"s5l8720x","cpid":34592,"bdid":0},{"name":"iPod touch 3","identifier":"iPod3,1","boards":[{"boardconfig":"n18ap","platform":"s5l8922x","cpid":35106,"bdid":2}],"boardconfig":"n18ap","platform":"s5l8922x","cpid":35106,"bdid":2},{"name":"iPod touch 4","identifier":"iPod4,1","boards":[{"boardconfig":"n81ap","platform":"s5l8930x","cpid":35120,"bdid":8}],"boardconfig":"n81ap","platform":"s5l8930x","cpid":35120,"bdid":8},{"name":"iPad 1","identifier":"iPad1,1","boards":[{"boardconfig":"k48ap","platform":"s5l8930x","cpid":35120,"bdid":2}],"boardconfig":"k48ap","platform":"s5l8930x","cpid":35120,"bdid":2},{"name":"iPad 2 (WiFi)","identifier":"iPad2,1","boards":[{"boardconfig":"k93ap","platform":"s5l8940x","cpid":35136,"bdid":4}],"boardconfig":"k93ap","platform":"s5l8940x","cpid":35136,"bdid":4},{"name":"iPad 2 (GSM)","identifier":"iPad2,2","boards":[{"boardconfig":"k94ap","platform":"s5l8940x","cpid":35136,"bdid":6}],"boardconfig":"k94ap","platform":"s5l8940x","cpid":35136,"bdid":6},{"name":"iPad 2 (CDMA)","identifier":"iPad2,3","boards":[{"boardconfig":"k95ap","platform":"s5l8940x","cpid":35136,"bdid":2}],"boardconfig":"k95ap","platform":"s5l8940x","cpid":35136,"bdid":2},{"name":"iPad 2 (Mid 2012)","identifier":"iPad2,4","boards":[{"boardconfig":"k93aap","platform":"s5l8942x","cpid":35138,"bdid":6}],"boardconfig":"k93aap","platform":"s5l8942x","cpid":35138,"bdid":6},{"name":"iPad 3 (WiFi)","identifier":"iPad3,1","boards":[{"boardconfig":"j1ap","platform":"s5l8945x","cpid":35141,"bdid":0}],"boardconfig":"j1ap","platform":"s5l8945x","cpid":35141,"bdid":0},{"name":"iPad 3 (CDMA)","identifier":"iPad3,2","boards":[{"boardconfig":"j2ap","platform":"s5l8945x","cpid":35141,"bdid":2}],"boardconfig":"j2ap","platform":"s5l8945x","cpid":35141,"bdid":2},{"name":"iPad 3 (GSM)","identifier":"iPad3,3","boards":[{"boardconfig":"j2aap","platform":"s5l8945x","cpid":35141,"bdid":4}],"boardconfig":"j2aap","platform":"s5l8945x","cpid":35141,"bdid":4},{"name":"Apple TV 2G","identifier":"AppleTV2,1","boards":[{"boardconfig":"k66ap","platform":"s5l8930x","cpid":35120,"bdid":16}],"boardconfig":"k66ap","platform":"s5l8930x","cpid":35120,"bdid":16},{"name":"Apple TV 3","identifier":"AppleTV3,1","boards":[{"boardconfig":"J33AP","platform":"s5l8942x","cpid":35138,"bdid":8}],"boardconfig":"J33AP","platform":"s5l8942x","cpid":35138,"bdid":8},{"name":"iPod touch 5","identifier":"iPod5,1","boards":[{"boardconfig":"n78ap","platform":"s5l8942x","cpid":35138,"bdid":0}],"boardconfig":"n78ap","platform":"s5l8942x","cpid":35138,"bdid":0},{"name":"iPhone 4 (GSM / 2012)","identifier":"iPhone3,2","boards":[{"boardconfig":"n90bap","platform":"s5l8930x","cpid":35120,"bdid":4}],"boardconfig":"n90bap","platform":"s5l8930x","cpid":35120,"bdid":4},{"name":"iPhone 5 (GSM)","identifier":"iPhone5,1","boards":[{"boardconfig":"N41AP","platform":"s5l8950x","cpid":35152,"bdid":0}],"boardconfig":"N41AP","platform":"s5l8950x","cpid":35152,"bdid":0},{"name":"iPhone 5 (Global)","identifier":"iPhone5,2","boards":[{"boardconfig":"N42AP","platform":"s5l8950x","cpid":35152,"bdid":2}],"boardconfig":"N42AP","platform":"s5l8950x","cpid":35152,"bdid":2},{"name":"iPad Mini (WiFi)","identifier":"iPad2,5","boards":[{"boardconfig":"p105ap","platform":"s5l8942x","cpid":35138,"bdid":10}],"boardconfig":"p105ap","platform":"s5l8942x","cpid":35138,"bdid":10},{"name":"iPad Mini (GSM)","identifier":"iPad2,6","boards":[{"boardconfig":"p106ap","platform":"s5l8942x","cpid":35138,"bdid":12}],"boardconfig":"p106ap","platform":"s5l8942x","cpid":35138,"bdid":12},{"name":"iPad Mini (Global)","identifier":"iPad2,7","boards":[{"boardconfig":"p107ap","platform":"s5l8942x","cpid":35138,"bdid":14}],"boardconfig":"p107ap","platform":"s5l8942x","cpid":35138,"bdid":14},{"name":"iPad 4 (WiFi)","identifier":"iPad3,4","boards":[{"boardconfig":"P101AP","platform":"s5l8955x","cpid":35157,"bdid":0}],"boardconfig":"P101AP","platform":"s5l8955x","cpid":35157,"bdid":0},{"name":"iPad 4 (GSM)","identifier":"iPad3,5","boards":[{"boardconfig":"P102AP","platform":"s5l8955x","cpid":35157,"bdid":2}],"boardconfig":"P102AP","platform":"s5l8955x","cpid":35157,"bdid":2},{"name":"iPad 4 (Global)","identifier":"iPad3,6","boards":[{"boardconfig":"P103AP","platform":"s5l8955x","cpid":35157,"bdid":4}],"boardconfig":"P103AP","platform":"s5l8955x","cpid":35157,"bdid":4},{"name":"iPhone 5s (Global)","identifier":"iPhone6,2","boards":[{"boardconfig":"N53AP","platform":"s5l8960x","cpid":35168,"bdid":2}],"boardconfig":"N53AP","platform":"s5l8960x","cpid":35168,"bdid":2},{"name":"iPhone 5c (GSM)","identifier":"iPhone5,3","boards":[{"boardconfig":"N48AP","platform":"s5l8950x","cpid":35152,"bdid":10}],"boardconfig":"N48AP","platform":"s5l8950x","cpid":35152,"bdid":10},{"name":"iPhone 5c (Global)","identifier":"iPhone5,4","boards":[{"boardconfig":"N49AP","platform":"s5l8950x","cpid":35152,"bdid":14}],"boardconfig":"N49AP","platform":"s5l8950x","cpid":35152,"bdid":14},{"name":"iPhone 5s (GSM)","identifier":"iPhone6,1","boards":[{"boardconfig":"N51AP","platform":"s5l8960x","cpid":35168,"bdid":0}],"boardconfig":"N51AP","platform":"s5l8960x","cpid":35168,"bdid":0},{"name":"iPad Mini 2 (WiFi)","identifier":"iPad4,4","boards":[{"boardconfig":"J85AP","platform":"s5l8960x","cpid":35168,"bdid":10}],"boardconfig":"J85AP","platform":"s5l8960x","cpid":35168,"bdid":10},{"name":"iPad Mini 2 (Cellular)","identifier":"iPad4,5","boards":[{"boardconfig":"J86AP","platform":"s5l8960x","cpid":35168,"bdid":12}],"boardconfig":"J86AP","platform":"s5l8960x","cpid":35168,"bdid":12},{"name":"iPad Air (WiFi)","identifier":"iPad4,1","boards":[{"boardconfig":"J71AP","platform":"s5l8960x","cpid":35168,"bdid":16}],"boardconfig":"J71AP","platform":"s5l8960x","cpid":35168,"bdid":16},{"name":"iPad Air (Cellular)","identifier":"iPad4,2","boards":[{"boardconfig":"J72AP","platform":"s5l8960x","cpid":35168,"bdid":18}],"boardconfig":"J72AP","platform":"s5l8960x","cpid":35168,"bdid":18},{"name":"iPad Air (China)","identifier":"iPad4,3","boards":[{"boardconfig":"J73AP","platform":"s5l8960x","cpid":35168,"bdid":20}],"boardconfig":"J73AP","platform":"s5l8960x","cpid":35168,"bdid":20},{"name":"iPad Mini 2 (China)","identifier":"iPad4,6","boards":[{"boardconfig":"J87AP","platform":"s5l8960x","cpid":35168,"bdid":14}],"boardconfig":"J87AP","platform":"s5l8960x","cpid":35168,"bdid":14},{"name":"iPhone 6+","identifier":"iPhone7,1","boards":[{"boardconfig":"N56AP","platform":"t7000","cpid":28672,"bdid":4}],"boardconfig":"N56AP","platform":"t7000","cpid":28672,"bdid":4},{"name":"iPhone 6","identifier":"iPhone7,2","boards":[{"boardconfig":"N61AP","platform":"t7000","cpid":28672,"bdid":6}],"boardconfig":"N61AP","platform":"t7000","cpid":28672,"bdid":6},{"name":"iPad Mini 3 (WiFi)","identifier":"iPad4,7","boards":[{"boardconfig":"J85mAP","platform":"s5l8960x","cpid":35168,"bdid":50}],"boardconfig":"J85mAP","platform":"s5l8960x","cpid":35168,"bdid":50},{"name":"iPad Mini 3 (Cellular)","identifier":"iPad4,8","boards":[{"boardconfig":"J86mAP","platform":"s5l8960x","cpid":35168,"bdid":52}],"boardconfig":"J86mAP","platform":"s5l8960x","cpid":35168,"bdid":52},{"name":"iPad Mini 3 (China)","identifier":"iPad4,9","boards":[{"boardconfig":"J87mAP","platform":"s5l8960x","cpid":35168,"bdid":54}],"boardconfig":"J87mAP","platform":"s5l8960x","cpid":35168,"bdid":54},{"name":"iPad Air 2 (WiFi)","identifier":"iPad5,3","boards":[{"boardconfig":"J81AP","platform":"t7001","cpid":28673,"bdid":6}],"boardconfig":"J81AP","platform":"t7001","cpid":28673,"bdid":6},{"name":"iPad Air 2 (Cellular)","identifier":"iPad5,4","boards":[{"boardconfig":"J82AP","platform":"t7001","cpid":28673,"bdid":2}],"boardconfig":"J82AP","platform":"t7001","cpid":28673,"bdid":2},{"name":"iPod touch 6","identifier":"iPod7,1","boards":[{"boardconfig":"N102AP","platform":"t7000","cpid":28672,"bdid":16}],"boardconfig":"N102AP","platform":"t7000","cpid":28672,"bdid":16},{"name":"iPad Mini 4 (WiFi)","identifier":"iPad5,1","boards":[{"boardconfig":"J96AP","platform":"t7000","cpid":28672,"bdid":8}],"boardconfig":"J96AP","platform":"t7000","cpid":28672,"bdid":8},{"name":"iPad Mini 4 (Cellular)","identifier":"iPad5,2","boards":[{"boardconfig":"J97AP","platform":"t7000","cpid":28672,"bdid":10}],"boardconfig":"J97AP","platform":"t7000","cpid":28672,"bdid":10},{"name":"iPhone 6s","identifier":"iPhone8,1","boards":[{"boardconfig":"N71AP","platform":"s8000","cpid":32768,"bdid":4},{"boardconfig":"N71mAP","platform":"s8003","cpid":32771,"bdid":4}],"boardconfig":"N71AP","platform":"s8000","cpid":32768,"bdid":4},{"name":"Apple TV 4 (2015)","identifier":"AppleTV5,3","boards":[{"boardconfig":"J42dAP","platform":"t7000","cpid":28672,"bdid":52}],"boardconfig":"J42dAP","platform":"t7000","cpid":28672,"bdid":52},{"name":"iPhone 8 (Global)","identifier":"iPhone10,1","boards":[{"boardconfig":"D20AP","platform":"t8015","cpid":32789,"bdid":2}],"boardconfig":"D20AP","platform":"t8015","cpid":32789,"bdid":2},{"name":"iPhone 8 (GSM)","identifier":"iPhone10,4","boards":[{"boardconfig":"D201AP","platform":"t8015","cpid":32789,"bdid":10}],"boardconfig":"D201AP","platform":"t8015","cpid":32789,"bdid":10},{"name":"iPhone 8 Plus (GSM)","identifier":"iPhone10,5","boards":[{"boardconfig":"D211AP","platform":"t8015","cpid":32789,"bdid":12}],"boardconfig":"D211AP","platform":"t8015","cpid":32789,"bdid":12},{"name":"iPhone 8 Plus (Global)","identifier":"iPhone10,2","boards":[{"boardconfig":"D21AP","platform":"t8015","cpid":32789,"bdid":4}],"boardconfig":"D21AP","platform":"t8015","cpid":32789,"bdid":4},{"name":"iPhone X (Global)","identifier":"iPhone10,3","boards":[{"boardconfig":"D22AP","platform":"t8015","cpid":32789,"bdid":6}],"boardconfig":"D22AP","platform":"t8015","cpid":32789,"bdid":6},{"name":"iPhone X (GSM)","identifier":"iPhone10,6","boards":[{"boardconfig":"D221AP","platform":"t8015","cpid":32789,"bdid":14}],"boardconfig":"D221AP","platform":"t8015","cpid":32789,"bdid":14},{"name":"iPhone XS Max","identifier":"iPhone11,6","boards":[{"boardconfig":"D331pAP","platform":"t8020","cpid":32800,"bdid":26}],"boardconfig":"D331pAP","platform":"t8020","cpid":32800,"bdid":26},{"name":"iPhone XS","identifier":"iPhone11,2","boards":[{"boardconfig":"D321AP","platform":"t8020","cpid":32800,"bdid":14}],"boardconfig":"D321AP","platform":"t8020","cpid":32800,"bdid":14},{"name":"iPhone XS Max (China)","identifier":"iPhone11,4","boards":[{"boardconfig":"D331AP","platform":"t8020","cpid":32800,"bdid":10}],"boardconfig":"D331AP","platform":"t8020","cpid":32800,"bdid":10},{"name":"iPhone XR","identifier":"iPhone11,8","boards":[{"boardconfig":"N841AP","platform":"t8020","cpid":32800,"bdid":12}],"boardconfig":"N841AP","platform":"t8020","cpid":32800,"bdid":12},{"name":"iPad Mini 5 (WiFi)","identifier":"iPad11,1","boards":[{"boardconfig":"J210AP","platform":"t8020","cpid":32800,"bdid":20}],"boardconfig":"J210AP","platform":"t8020","cpid":32800,"bdid":20},{"name":"iPad Mini 5 (Cellular)","identifier":"iPad11,2","boards":[{"boardconfig":"J211AP","platform":"t8020","cpid":32800,"bdid":22}],"boardconfig":"J211AP","platform":"t8020","cpid":32800,"bdid":22},{"name":"iPad Air 3 (WiFi)","identifier":"iPad11,3","boards":[{"boardconfig":"J217AP","platform":"t8020","cpid":32800,"bdid":28}],"boardconfig":"J217AP","platform":"t8020","cpid":32800,"bdid":28},{"name":"iPad Air 3 (Cellular)","identifier":"iPad11,4","boards":[{"boardconfig":"J218AP","platform":"t8020","cpid":32800,"bdid":30}],"boardconfig":"J218AP","platform":"t8020","cpid":32800,"bdid":30}]'''
# d = json.loads(infojson)
# for l in d:
#     print(l['identifier'])
    # if len(l['boards']) > 1:
    #     print(l)


data = '''=======================================
::
:: iBootStage2 for n71m, Copyright 2007-2020, Apple Inc.
::
::	Local boot, Board 0x4 (n71map)/Rev 0x6
::
::	BUILD_TAG: iBoot-6723.18.89
::
::	BUILD_STYLE: RELEASE
::
::	USB_SERIAL_NUMBER: SDOM:01 CPID:8003 CPRV:01 CPFM:03 SCEP:01 BDID:04 ECID:000161E610E9AF26 IBFL:1D SRNM:[FK1VM0KJHFLV]
::
=======================================
'''

# pattern = r'iBoot for (.+?), Copyright'
# print(re.findall(pattern, data))
# pattern = r'iBoot-(\d+\.\d+\.\d+)'
# print(re.findall(pattern, data))
# pattern = r'BUILD_STYLE: (.+)'
# print(re.findall(pattern, data))
# pattern = r'CPID:(\d+)'
# print(re.findall(r'ECID:([a-zA-Z0-9]+)', data))
# print(re.findall(r'SRNM:\[(.+)\]', data))
# res = re.findall(r"([a-zA-Z0-9]{12})\]", data)
# print(res)