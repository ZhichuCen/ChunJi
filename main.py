# -*- coding: utf-8 -*-
import wave
import pyaudio
import keyboard
from playsound import playsound
from sasr import sasr
from tts import tts


class ChunJi:
    def __init__(self):
        self.space_result_text = ""
        self.space_result = {}
        self.cursor = 0
        keyboard.add_hotkey('space', self.on_space_press)
        keyboard.add_hotkey('alt', self.on_alt_press)

    def on_space_press(self):
        self.audio_record('space')
        self.space_result = eval(sasr())
        self.space_result_text = self.space_result["result"]["text"]
        if self.space_result["result"]["score"] < 0.6:
            self.speech("准确率低，建议检查")
        print(self.space_result)
        print(self.space_result_text)

    def on_alt_press(self):
        pass

    def audio_record(self, key):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率

        p = pyaudio.PyAudio()
        # 创建音频流
        stream = p.open(format=FORMAT,  # 音频流wav格式
                        channels=CHANNELS,  # 单声道
                        rate=RATE,  # 采样率16000
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Start Recording...")

        frames = []  # 录制的音频流
        # 录制音频数据
        while True:
            if keyboard.is_pressed(key):
                data = stream.read(CHUNK)
                frames.append(data)
            else:
                break

        # 录制完成
        stream.stop_stream()
        stream.close()
        p.terminate()

        print("Recording Done...")

        # 保存音频文件
        wf = wave.open('audio.pcm', 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def speech(self, text):
        tts(text)
        playsound('tts.wav')


if __name__ == '__main__':
    ChunJi_1 = ChunJi()
    keyboard.wait('esc')
