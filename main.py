# -*- coding: utf-8 -*-
import os
import sys
import wave

import keyboard
import pyaudio
from playsound import playsound

from sasr import sasr
from tts import tts

PUNC_FULL = {'。': '句号', '，': '逗号', '、': '顿号', ';': '分号',
             '：': '冒号', '？': '问号', '！': '感叹号',
             '“': '左引号', '”': '右引号', '\n': '换行',
             '（': '左括号', '）': '右括号',
             '——': '破折号', '—': '连接号', '-': '减号',
             '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号'
             }

PUNC_HALF = {'；': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号', '\n': '换行',
             '(': '左括号', ')': '右括号', '...': '省略号', '.': '点', '"': '双引号', "'": '单引号',
             }

PUNC = {'。': '句号', '，': '逗号', '、': '顿号', ';': '分号', '：': '冒号', '？': '问号', '！': '感叹号',
        '“': '左引号', '”': '右引号', '\n': '换行', '（': '左括号', '）': '右括号', '——': '破折号', '—': '连接号', '-': '减号',
        '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号',
        '；': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号', '(': '左括号', ')': '右括号',
        '...': '省略号', '.': '点', '"': '双引号', "'": '单引号'}


# GEN_PUNC = {'。': '句号'}


class ChunJi:
    def __init__(self):
        self.last_undo = ""
        self.can_redo = False
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
        # self.saved = True
        self.previous_saved = ""
        self.log = []
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

            elif self.pending == '朗读选择':
                self.insta_read_method()

            # elif self.pending == '移动光标':
            #     self.move_cursor_to()

        else:
            if self.mode == "Command":
                self.command_method()
            elif self.mode == "Insert":
                self.insert_method()

    def command_method(self):
        if self.result_text in ['打字', '输入', '键入']:
            if not self.have_file:
                self.no_file()
            else:
                self.mode = "Insert"
                self.speech("当前模式：输入")
        elif '输入' in self.result_text:
            self.result_text = self.result_text.replace('输入', '', 1)
            self.insert_method()
        #
        # elif self.result_text in ['朗读上一句', '读上一句']:
        #     self.read_content('上一句')
        # elif self.result_text in ['朗读下一句', '读下一句']:
        #     self.read_content('下一句')
        # elif self.result_text in ['朗读全文', '全文朗读', '读全文']:
        #     self.read_content('全文')

        elif self.result_text in ['朗读', '读']:
            self.read_aloud_method()

        elif '朗读' in self.result_text or '读' in self.result_text:
            self.insta_read_method()

        # elif self.result_text in ['移动', '移动光标']:
        #     self.move_cursor_method()

        elif '移动' in self.result_text or '光标' in self.result_text:
            self.move_cursor_method()

        elif self.result_text in ['撤销', ' 撤回']:
            self.undo()

        elif self.result_text in ['重做', '取消撤回', '还原']:
            self.redo()

        elif self.result_text in ["保存", '存储']:
            self.save_file()

        elif self.result_text in ['退出', '关闭']:
            self.exit()

        else:
            self.speech('无效命令')

    def insert_method(self):
        if self.result_text == "退出":
            self.mode = "Command"
            self.speech("当前模式：控制")
        elif not self.have_file:
            self.no_file()
        else:
            self.log.append((self.text, self.cursor))

            if self.result_text in PUNC_FULL.values():
                self.result_text = list(PUNC_FULL.keys())[list(PUNC_FULL.values()).index(self.result_text)]
                self.speech('插入标点:' + PUNC[self.result_text])

            left = self.text[0:self.cursor]
            right = self.text[self.cursor:-1]
            self.cursor += len(self.result_text)
            self.text = left + self.result_text + right
            # self.saved = False
            print(self.text)

    def move_cursor_method(self):
        # self.pending = '移动光标'

        # self.speech('请选择光标将移动的位置')
        if '头' in self.result_text or '开' in self.result_text:
            self.log.append((self.text, self.cursor))
            self.cursor = 0
            self.speech('光标已移动至文档开头')

        elif '尾' in self.result_text or '末' in self.result_text:
            self.log.append((self.text, self.cursor))
            self.cursor = len(self.text)
            self.speech('光标已移动至文档末尾')

        elif ('前' in self.result_text or '上' in self.result_text) and ('字' in self.result_text):
            self.log.append((self.text, self.cursor))
            self.cursor -= self.abstract_digit(self.result_text)
            if self.cursor < 0:
                self.cursor = 0
                self.speech('警告：超出文件范围，光标已移动至文档开头')
            else:
                self.speech('光标已前移' + str(self.abstract_digit(self.result_text)) + '字')

        elif ('后' in self.result_text or '下' in self.result_text) and ('字' in self.result_text):
            self.log.append((self.text, self.cursor))
            self.cursor += self.abstract_digit(self.result_text)
            if self.cursor > len(self.text):
                self.cursor = len(self.text)
                self.speech('警告：超出文件范围，光标已移动至文档末尾')
            else:
                self.speech('光标已后移' + str(self.abstract_digit(self.result_text)) + '字')

        # elif

    # def move_cursor_to(self):

    def undo(self):
        self.last_undo = self.text
        self.can_redo = True
        self.text, self.cursor = self.log.pop()
        self.speech('已撤销')

    def redo(self):
        if self.can_redo:
            self.log.append((self.text, self.cursor))
            self.text = self.last_undo
            self.can_redo = False
            self.speech('已重做')
        else:
            self.speech('无法重做')

    def read_aloud_method(self):
        self.speech('请选择要朗读的内容')
        self.pending = '朗读选择'

    def insta_read_method(self):
        if ('全文' in self.result_text) or ('所有' in self.result_text) or ('全' in self.result_text):
            self.read_content('全文')
        elif ('上一句' in self.result_text) or ('上句' in self.result_text) or ('前一句' in self.result_text) or (
                '前句' in self.result_text):
            self.read_content('上一句')
        elif ('下一句' in self.result_text) or ('下句' in self.result_text) or ('后一句' in self.result_text) or (
                '后句' in self.result_text):
            self.read_content('下一句')
        elif ('上一段' in self.result_text) or ('上段' in self.result_text) or ('前一段' in self.result_text) or (
                '前段' in self.result_text):
            self.read_content('上一段')
        elif ('下一段' in self.result_text) or ('下段' in self.result_text) or ('后一段' in self.result_text) or (
                '后段' in self.result_text):
            self.read_content('下一段')
        else:
            self.speech('无法朗读内容')

    # def select_read_method(self):
    #
    #     if self.result_text in ['全文', '所有', '全']:
    #         self.read_content('全文')
    #     elif self.result_text in ['上一句', '上句']:
    #         self.read_content('上一句')
    #     elif self.result_text in ['下一句', '下句']:
    #         self.read_content('下一句')
    #     elif self.result_text in ['上一段', '上段']:
    #         self.read_content('上一段')
    #     elif self.result_text in ['下一段', '下段']:
    #         self.read_content('下一段')
    #
    #     else:
    #         self.speech('请正确选择朗读内容')

    def read_content(self, content):
        self.pending = ''

        if content == '全文':
            self.speech(self.text, read_punc=True)

        elif content == '上一句':
            self.speech(self.selector('上一句'), read_punc=True)
        elif content == '下一句':
            self.speech(self.selector('下一句'), read_punc=True)
        elif content == '上一段':
            self.speech(self.selector('上一段'), read_punc=True)
        elif content == '下一段':
            self.speech(self.selector('下一段'), read_punc=True)

    def delete_method(self, content):

        if content == '上一句':
            pass
        elif content == '下一句':
            pass

    def selector(self, area):

        if area == '全文':
            return self.text
        elif area == '上一句':
            left = self.text[0:self.cursor]
            l = len(left)
            for i in range(l):
                t = left[-1 - i]
                if t in PUNC.keys() and i != 0 and i != 1:
                    return left[-i:]
            return left

        elif area == '下一句':
            right = self.text[self.cursor:-1]
            r = len(right)
            for i in range(r):
                t = right[i]
                if t in PUNC.keys() and i != 0 and i != 1:
                    return right[:i + 1]
            return right

        elif area == '上一段':
            left = self.text[0:self.cursor]
            l = len(left)
            for i in range(l):
                t = left[-1 - i]
                if t == '\n' and i != 0 and i != 1:
                    return left[-i:]
            return left

        elif area == '下一段':
            right = self.text[self.cursor:-1]
            r = len(right)
            for i in range(r):
                t = right[i]
                if t == '\n' and i != 0 and i != 1:
                    return right[:i + 1]
            return right

    def save_file(self):
        with open(self.name, 'w') as f:
            f.write(self.text)
        # self.saved = True
        self.previous_saved = self.text
        self.speech('保存成功')

    def exit(self):
        if self.text != self.previous_saved:
            self.speech('警告：当前文件未保存')
        else:
            self.speech('欢迎下次使用', block=True)
            sys.exit()

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
        self.speech("将命名为：" + self.unconfirmed_name + "。确认请说：'是'", filename=True)
        self.pending = "命名确认"

    def confirm_name(self):
        if self.result_text in ['是', '确认', '是的']:
            self.name = self.unconfirmed_name
            self.have_file = True
            self.pending = ""
            self.log.append((self.text, self.cursor))
            # self.saved = False
            self.speech("新建成功。当前模式：控制")
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
            self.speech(self.read_file_tts, filename=True)
            self.pending = "选文件"
            print(self.open_list)

    def choose_file(self):
        # try:
        self.result_text = self.abstract_digit(self.result_text)
        index = int(self.result_text) - 1
        # except ValueError:
        #     self.speech("请说数字")
        # else:
        self.name = self.open_list[index]
        with open(self.name, "r") as f:
            self.text = f.read()

        self.pending = ""
        self.have_file = True
        self.cursor = len(self.text)
        self.previous_saved = self.text
        self.log.append((self.text, self.cursor))
        self.speech('已打开文件:' + self.name + '。当前模式：控制', filename=True)

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
    def speech(text, block=False, filename=False, read_punc=False):
        if filename:
            if "." in text:
                text = text.replace(".", "点")

        if read_punc:
            text = text.replace(' ', '空格')
            for i in PUNC.keys():
                text = text.replace(i, ' ' + PUNC[i] + ' ')

        print(text)
        tts(text)
        playsound("tts.wav", block=block)

    @staticmethod
    def abstract_digit(text):
        import chinese2digits as c2d
        return int(c2d.takeNumberFromString(text)['digitsStringList'][0])


if __name__ == "__main__":
    chunji = ChunJi()
    keyboard.wait("esc")
