'''
该文件对音频文件进行语音转写，用在了we_response.py中
'''
import requests
import json
import pyaudio
import wave
import base64
import os
import keyboard
import threading

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 60
q = False

def read_key():
    global q
    while True:
        if keyboard.is_pressed(' '):  
            q = False
        else:
            q = True
            break

def rec(file_name):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音,请说话......")

    frames = []

    global q

    t = threading.Thread(target=read_key)
    t.start()

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if q:
            break

    print("录音结束!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

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


if __name__ == "__main__":
    while True:
        if keyboard.is_pressed(' '):
            rec("temp.wav")
            break
    token = Gettokent()
    res = BaiduYuYin("temp.wav", token)
    print(res + "\n")
    print(get_keys(res))
