# -*- encoding:utf-8 -*-

'''
该文件使用讯飞进行实时语音转写
'''

import chunk
import sys
import hashlib
from hashlib import sha1
import hmac
import base64
from socket import *
import json, time, threading
from websocket import create_connection
import websocket
from urllib.parse import quote
import logging
import pyaudio
import wave
import keyboard

# reload(sys)
# sys.setdefaultencoding("utf8")
logging.basicConfig()

#讯飞参数
base_url = "ws://rtasr.xfyun.cn/v1/ws"
app_id = "539e5c09"
api_key = "139f309eadd3b64ef434985c8617c3fb"
file_path = "test_1.pcm"

pd = "edu"

end_tag = "{\"end\": true}"

#读取音频流的参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# RECORD_SECONDS = 60

class Client():
    #连接websocket
    def __init__(self):
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    #读取实时音频并发送到服务端进行语音识别
    def send(self, file_path):
        p = pyaudio.PyAudio()
        #打开语音流
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("开始录音,请说话......")

        frames = []

        # file_object = open(file_path, 'rb')

        try:
            index = 1
            while True:
                # chunk = file_object.read(CHUNK)
                #读取音频流
                chunk = stream.read(CHUNK)
                frames.append(chunk)
                #当空格键按下时停止语音识别
                if keyboard.is_pressed(' '):
                    break
                #发送语音流
                self.ws.send(chunk)
                index += 1
                time.sleep(0.04)
        finally:
            #结束对音频流的读取并保存至file_path中
            # file_object.close()
            print("录音结束!")
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

        self.ws.send(bytes(end_tag.encode('utf-8')))
        print("send end tag success")

#解析语音的转写结果
    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    # result_2 = json.loads(result_1["cn"])
                    # result_3 = json.loads(result_2["st"])
                    # result_4 = json.loads(result_3["rt"])
                    data = json.loads(result_1["data"])
                    # print(data)
                    mid_ls = data["cn"]["st"]["rt"][0]["ws"]
                    res = ""
                    for i in range(len(mid_ls)):
                        if i < len(mid_ls) - 1:
                            res += mid_ls[i + 1]["cw"][0]["w"]
                        else:
                            res += mid_ls[0]["cw"][0]["w"]
                    print("rtasr result: " + res)

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")
    #关闭websocket
    def close(self):
        self.ws.close()
        print("connection closed")


if __name__ == '__main__':
    client = Client()
    client.send(file_path)
