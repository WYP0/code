from pydub import AudioSegment

#从.wav文件转成.mp3文件
def trans_wav_to_mp3(filepath):
    song = AudioSegment.from_wav(filepath)
    song.export("temp.mp3", format="mp3")
trans_wav_to_mp3("temp.wav")