# -*- coding: utf-8 -*-
import wave
import pyaudio
import keyboard
from playsound import playsound
from sasr import sasr
from tts import tts


class ChunJi:
    def __init__(self):
        self.result_text = ""
        self.result = {}
        self.cursor = 0
        self.mode = 'Command'
        self.have_file = False
        self.pending = ""
        self.text = ""
        keyboard.add_hotkey('space', self.on_space_press)
        keyboard.add_hotkey('alt', self.on_alt_press)

    def on_space_press(self):
        self.audio_record('space')
        self.result = eval(sasr())
        self.result_text = self.result["result"]["text"]
        if self.result["result"]["score"] < 0.6:
            self.speech("准确率低，建议检查")
        print(self.result)
        print(self.result_text)

    def on_alt_press(self):
        self.audio_record('alt')
        self.result = eval(sasr())
        self.result_text = self.result["result"]["text"]
        if self.result["result"]["score"] < 0.6:
            self.speech("准确率低，建议检查")
        elif self.pending:
            if self.pending == '打开或新建':
                self.response_file()


        else:
            if self.mode == 'Command':
                pass
            elif self.mode == 'Insert':
                self.insert_method()

    def insert_method(self):
        if self.result_text == "退出":
            self.mode = 'Command'
        elif not self.have_file:
            self.speech("请先打开或新建文件")
            self.no_file()
        else:
            left = self.text[0:self.cursor]
            right = self.text[self.cursor:-1]
            self.cursor += len(self.result_text)
            self.text = left + self.result_text + right

    def response_file(self):
        if self.result_text == '打开':
            self.pending = ''
            self.open_file()

        elif self.result_text == '新建':
            self.pending = ''
            self.new_file()

        else:
            self.speech('错误，请选择打开或新建')

    def no_file(self):
        self.speech('打开或新建')
        self.pending = '打开或新建'

    def open_file:

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
