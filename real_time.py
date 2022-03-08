import websocket

import threading
import time
import uuid
import json
import sys
import pyaudio
import keyboard
import wave

import const

pcm_file = "16k-0.pcm"

"""
1. 连接 ws_app.run_forever()
2. 连接成功后发送数据 on_open()
2.1 发送开始参数帧 send_start_params()
2.2 发送音频数据帧 send_audio()
2.3 库接收识别结果 on_message()
2.4 发送结束帧 send_finish()
3. 关闭连接 on_close()
库的报错 on_error()
"""


def send_start_params(ws):
    """
    开始参数帧
    :param websocket.WebSocket ws:
    :return:
    """
    req = {
        "type": "START",
        "data": {
            "appid": const.APPID,  # 网页上的appid
            "appkey": const.APPKEY,  # 网页上的appid对应的appkey
            "dev_pid": const.DEV_PID,  # 识别模型
            "cuid": "python",  # 随便填不影响使用。机器的mac或者其它唯一id，百度计算UV用。
            "sample": 16000,  # 固定参数
            "format": "pcm"  # 固定参数
        }
    }
    body = json.dumps(req)
    ws.send(body, websocket.ABNF.OPCODE_TEXT)


def send_audio(ws):
    """
    发送二进制音频数据，注意每个帧之间需要有间隔时间
    :param  websocket.WebSocket ws:
    :return:
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音,请说话......")
    frames = []
    while True:
        chunk = stream.read(CHUNK)
        frames.append(chunk)
        if keyboard.is_pressed(' '):
            break
        ws.send(chunk, websocket.ABNF.OPCODE_BINARY)
        time.sleep(0.04)
    print("录音结束!")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(pcm_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    ws_app.close()


def on_open(ws):
    """
    连接后发送数据帧
    :param  websocket.WebSocket ws:
    :return:
    """

    def run(*args):
        """
        发送数据帧
        :param args:
        :return:
        """
        send_start_params(ws)
        send_audio(ws)

    threading.Thread(target=run).start()


def on_message(ws, message):
    """
    接收服务端返回的消息
    :param ws:
    :param message: json格式，自行解析
    :return:
    """
    # res = str(message)
    res_dict = json.loads(message)
    if (res_dict["err_msg"] == 'OK'):
        if (res_dict["type"] != 'HEARTBREAT'):
            print(res_dict["result"])
    else:
        print(res_dict["err_msg"])


if __name__ == "__main__":
    # websocket.enableTrace(True)
    uri = const.URI + "?sn=" + str(uuid.uuid1())
    ws_app = websocket.WebSocketApp(uri,
                                    on_open=on_open,  # 连接建立后的回调
                                    on_message=on_message)  # 接收消息的回调
    ws_app.run_forever()