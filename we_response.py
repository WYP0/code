'''
该文件实现公众号的自动回复功能，集成了音频文件转写，实时语音识别等功能
'''
from dataclasses import replace
from email import message
from http import client
import re
import werobot
from werobot.replies import ImageReply
from werobot.replies import TextReply
from werobot.replies import VoiceReply
import pyaudio
import wave
import keyboard
import threading
import sys
import base64
import os
import requests
import json
from pydub import AudioSegment
import rtasr_python3_demo
from socket import *

token="python"  
robot = werobot.WeRoBot(token=token)
robot.config["APP_ID"] = "wxe82e6c26bf184238"
robot.config["APP_SECRET"]="efae10007d9831d30779ba7e5c03d332"
client = robot.client
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 60
q = False
start = True
source = []
target = []

#将.wav文件转为.mps文件
def trans_wav_to_mp3(filepath):
    song = AudioSegment.from_wav(filepath)
    song.export("temp.mp3", format="mp3")

def BaiduYuYin(fileurl, token):
    try:
        RATE = "16000"                  #采样率16KHz
        FORMAT = "wav"                  #wav格式
        CUID = "wate_play"
        DEV_PID = "1536"                #无标点普通话

        # 以字节格式读取文件之后进行编码
        with open(fileurl, "rb") as f:
            speech = base64.b64encode(f.read()).decode('utf8')

        size = os.path.getsize(fileurl)
        headers = {'Content-Type': 'application/json'}
        url = "https://vop.baidu.com/server_api"
        data = {
            "format": FORMAT,
            "rate": RATE,
            "dev_pid": DEV_PID,
            "speech": speech,
            "cuid": CUID,
            "len": size,
            "channel": 1,
            "token": token,
        }
        req = requests.post(url, json.dumps(data), headers)
        result = json.loads(req.text)
        return result["result"][0][:-1]
    except:
        return 'cannot recognize'

#获取百度API token
def Gettokent():
    baidu_server = "https://openapi.baidu.com/oauth/2.0/token?"
    grant_type = "client_credentials"
    #API Key
    client_id = "X72Nc5j9m08uVUKGebMcEq0G"
    #Secret Key
    client_secret = "BE4Bv2CepY7H7ibYe9LCeiV9OoAqrA39"

    #url
    url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(client_id, client_secret)
    # print(url)
    #获取token
    res = requests.post(url)
    # print(res.text)
    token = json.loads(res.text)["access_token"]
    return token


#简单的解析语音转写结果用以控制微信发送信息
def get_keys(res):
    size = len(res)
    key_ls = []
    key_sec = False
    key_get = False
    i = 0
    while i < size:
        if res[i:i+4] == "小爱同学":
            i = i+4
            key_sec = True
            continue
        if res[i:i+2] == "发送" and key_sec:
            i = i+2
            key_get = True
            continue
        if key_get:
            key_ls.append(res[i])
        i = i+1
    key = "".join(key_ls)
    return key

#当空格按下时录音至temp.wav，当'a'按下时，开始实时语音转写， 当'q'按下时停止语音相关功能
def voice_start():
    global start
    while True:
        if keyboard.is_pressed(' ') and start:
            start = False
            rec("temp.wav")
            # res = client.upload_media(robot.voice, "temp.wav")
            # print(res)
        if keyboard.is_pressed('a'):
            client = rtasr_python3_demo.Client()
            client.send("test.pcm")
        # if keyboard.is_pressed('s'):
            # client.send_text_message(source[-1], "hello")
        if keyboard.is_pressed('q'):
            sys.exit()

#用以控制读取时间，当空格键松开时录音结束
def read_key():
    global q
    while True:
        if keyboard.is_pressed(' '):  
            q = False
        else:
            q = True
            break

#录制音频
def rec(file_name):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("start recording...")

    frames = []

    global q, start

    #开启另一个线程用以检测是否结束录音
    t = threading.Thread(target=read_key)
    t.start()

    #开始录音
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if q:
            break

    print("stop recording!")
    #关闭音频流
    stream.stop_stream()
    stream.close()
    p.terminate()
    #将读取到的音频流
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    start = True 

#可以推送音乐
def music_data():
    music_list = [
        ["微信你不懂爱", "龚琳娜最新力作", "http://weixin.com/budongai.mp3",]
    ]
    # num = random.randint(0,2)
    return music_list[0]

#上传媒体素材到公众号并返回media_id
def get_media_ID(path, token, type):
    url='https://api.weixin.qq.com/cgi-bin/material/add_material'
    payload={
        'access_token':token,
        'type': type
    }
    data ={'media':open(path,'rb')}
    r=requests.post(url=url,params=payload,files=data)
    dict =r.json()
    # print(dict)
    return dict['media_id']

#获取当前媒体素材
def get_media_list(token):
    url="https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token="+token
    datas={
        "type":"voice",
        "offset":0,
        "count":20
    }
    data = json.dumps(datas)
    a=requests.post(url=url,data =data)
    dict = a.json()
    # print(a.text)
    return dict["item"][0]["media_id"]


if __name__ == "__main__":
    #开启新线程来实现语音相关功能
    voice = threading.Thread(target=voice_start)
    voice.start()
    access_token = client.get_access_token()
    # print(token)

    #订阅收到后回复
    @robot.subscribe
    def sub():
        return "thank you for your subscribe"

    #收到'music'文本信息后回复
    @robot.filter('music')
    def music():
        reply = music_data()
        return reply
    
    #收到'voice'文本信息后回复最近录入的语音信息
    @robot.filter("voice")
    def voice(message):
        # tokken = Gettokent()
        # res = BaiduYuYin("temp.wav", tokken)
        # reply = get_keys(res)
        trans_wav_to_mp3("temp.wav")
        get_media_ID("temp.mp3", access_token, 'voice')
        media_id = get_media_list(access_token)
        reply = VoiceReply(message=message, media_id = media_id)
        return reply

    #收到文本信息后保存并回复
    @robot.text
    def tex(message, session):
        length = str(len(session))
        session[length] = message.content
        reply = message.content
        print(message.source)
        global source, target
        source.append(message.source)
        target.append(message.target)
        # for i in session:
        #     print(session[i])
        return reply

    #收到图片信息后回复
    @robot.image
    def img(message, session):
        length = str(len(session))
        session[length] = message.MediaId
        media_id = get_media_ID("test.jpg", access_token, "image")
        reply = ImageReply(message=message, media_id = media_id)
        return reply

    #设定发送节点
    robot.config['HOST'] = '0.0.0.0'
    robot.config['PORT'] = 80
    robot.run()
