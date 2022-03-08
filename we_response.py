from dataclasses import replace
from http import client
import werobot
from werobot.replies import ImageReply
import pyaudio
import wave
import keyboard
import threading
import sys

token="python"  
robot = werobot.WeRoBot(token=token)
client = robot.client
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
RECORD_SECONDS = 60
q = False
start = True

def voice_start():
    global start
    while True:
        if keyboard.is_pressed(' ') and start:
            rec("temp.wav")
            start = False
        if keyboard.is_pressed('q'):
            sys.exit()

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

    global q, start

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
    start = True 

def music_data():
    music_list = [
        ["微信你不懂爱", "龚琳娜最新力作", "http://weixin.com/budongai.mp3",]
    ]
    # num = random.randint(0,2)
    return music_list[0]



if __name__ == "__main__":
    voice = threading.Thread(target=voice_start)
    voice.start()

    @robot.subscribe
    def sub():
        return "thank you for your subscribe"

    @robot.filter('music')
    def music():
        reply = music_data()
        return reply

    @robot.text
    def tex(message, session):
        length = str(len(session))
        session[length] = message.content
        reply = message.content
        print(message.source)
        # for i in session:
        #     print(session[i])
        return reply

    @robot.image
    def img(message, session):
        length = str(len(session))
        session[length] = message.MediaId
        reply = ImageReply(message=message, media_id = message.MediaId)
        return reply


    
    robot.config['HOST'] = '0.0.0.0'
    robot.config['PORT'] = 80
    robot.run()
