from pydub import AudioSegment

def trans_wav_to_mp3(filepath):
    song = AudioSegment.from_wav(filepath)
    song.export("temp.mp3", format="mp3")
trans_wav_to_mp3("temp.wav")