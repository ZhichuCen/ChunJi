# -*- coding: utf-8 -*-
import wave
import pyaudio
import keyboard
from playsound import playsound
from sasr import sasr
from tts import tts
import os


class ChunJi:
    def __init__(self):
        self.unconfirmed_name = ""
        self.open_list = []
        self.read_file_tts = ""
        self.result_text = ""
        self.result = {}
        self.cursor = 0
        self.mode = "Command"
        self.have_file = False
        self.pending = ""
        self.text = ""
        self.name = ""
        # keyboard.add_hotkey("alt", self.on_alt_press)
        keyboard.add_hotkey("space", self.on_space_press)

        self.welcome()

    def welcome(self):
        self.speech("欢迎使用唇记,请先打开或新建文件")
        self.no_file()

    # def on_space_press(self):
    #     self.audio_record("space")
    #     self.result = eval(sasr())
    #     self.result_text = self.result["result"]["text"]
    #     if self.result["result"]["score"] < 0.6:
    #         self.speech("准确率低，建议检查")
    #     print(self.result)
    #     print(self.result_text)

    def on_space_press(self):
        self.audio_record("space")
        self.result = eval(sasr())
        self.result_text = self.result["result"]["text"]
        print(self.result_text)
        if self.result["result"]["score"] < 0.6:
            self.speech("准确率低，建议检查")
        elif self.pending:

            if self.pending == "打开或新建":
                self.response_file()

            elif self.pending == "选文件":
                self.choose_file()

            elif self.pending == "命名":
                self.new_name()

            elif self.pending == "命名确认":
                self.confirm_name()

        else:
            if self.mode == "Command":
                self.command_method()
            elif self.mode == "Insert":
                self.insert_method()

    def command_method(self):
        if self.result_text == "输入":
            if not self.have_file:
                self.no_file()
            else:
                self.mode = "Insert"
                self.speech("当前模式：输入")

    def insert_method(self):
        if self.result_text == "退出":
            self.mode = "Command"
            self.speech("当前模式：控制")
        elif not self.have_file:
            self.no_file()
        else:
            left = self.text[0:self.cursor]
            right = self.text[self.cursor:-1]
            self.cursor += len(self.result_text)
            self.text = left + self.result_text + right
            print(self.text)

    def response_file(self):
        if self.result_text == "打开":
            self.pending = ""
            self.open_file()

        elif self.result_text == "新建":
            self.pending = ""
            self.new_file()

        else:
            self.speech("错误，请选择打开或新建")

    def new_file(self):
        self.speech("请命名")
        self.pending = "命名"

    def new_name(self):
        self.unconfirmed_name = self.result_text + ".txt"
        self.speech("将命名为：" + self.unconfirmed_name + "。确认请说：'是'")
        self.pending = "命名确认"

    def confirm_name(self):
        if self.result_text == "是":
            self.name = self.unconfirmed_name
            self.speech("新建成功")
            self.have_file = True
            self.pending = ""
        else:
            self.speech('请重新说出文件名')
            self.pending = "命名"

    def no_file(self):
        self.pending = "打开或新建"

    def open_file(self):
        count = 0
        for file in os.listdir():
            if os.path.splitext(file)[1] == ".txt":
                count += 1
                self.open_list.append(file)
                self.read_file_tts += str(count) + ":" + str(file) + "。"
        if count == 0:
            self.speech("当前目录下无txt文件")
        else:
            self.read_file_tts += "请说出文件对应的数字"
            self.speech(self.read_file_tts)
            self.pending = "选文件"
            print(self.open_list)

    def choose_file(self):
        try:
            self.result_text = self.chinese_to_digit(self.result_text)
            index = int(self.result_text) - 1
        except ValueError:
            self.speech("请说数字")
        else:
            self.name = self.open_list[index]
            with open(self.name, "r") as f:
                self.text = f.read()
            self.speech('已打开文件:' + self.name)
            self.pending = ""
            self.have_file = True

    @staticmethod
    def audio_record(key):
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

        print("开始录制...")

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

        print("录制完成...")

        # 保存音频文件
        wf = wave.open("audio.pcm", "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

    @staticmethod
    def speech(text, block=False):
        if "." in text:
            text = text.replace(".", "点")
        print(text)
        tts(text)
        playsound("tts.wav", block=block)

    @staticmethod
    def chinese_to_digit(text):
        import chinese2digits as c2d
        return c2d.takeNumberFromString(text)['replacedText']


if __name__ == "__main__":
    ChunJi_1 = ChunJi()
    keyboard.wait("esc")
