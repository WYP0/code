import re
from time import sleep
from os import system
import requests
from pywinauto.keyboard import send_keys   

if __name__ == '__main__':
    
    text = input()
    wechat_path = "C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    system('"{}"'.format(wechat_path))  # 打开微信

    send_keys('^f')  # 按下查找快捷键
    send_keys('文件传输助手')  #查找对象

    sleep(0.5)
    send_keys('{ENTER}')  # 按下回车键-进入聊天窗口
    sleep(0.5)

    send_keys('{}'.format(text))  # 输入聊天内容
    send_keys('{ENTER}')  # 按下回车键  点击发送