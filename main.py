# -*- coding: utf-8 -*-
import json
import os
import platform
import re
import sys
import wave

import keyboard
import numpy as np
import pyaudio

from sasr import sasr
from tts import tts

PUNC_FULL = {'。': '句号', '，': '逗号', '、': '顿号', '；': '分号', '    ': '空两格',
             '：': '冒号', '？': '问号', '！': '感叹号',
             '“': '左引号', '”': '右引号', '\n': '回车',
             '（': '左括号', '）': '右括号',
             '——': '破折号', '—': '连接号', '-': '减号',
             '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号'
             }

PUNC_HALF = {';': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号', '\n': '回车',
             '(': '左括号', ')': '右括号', '...': '省略号', '.': '点', '"': '双引号', "'": '单引号',
             }

PUNC = {'。': '句号', '，': '逗号', '、': '顿号', ';': '分号', '：': '冒号', '？': '问号', '！': '感叹号', '    ': '空两格',
        '“': '左引号', '”': '右引号', '\n': '回车', '（': '左括号', '）': '右括号', '——': '破折号', '—': '连接号', '-': '减号',
        '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号',
        '；': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号', '(': '左括号', ')': '右括号',
        '...': '省略号', '.': '点', '"': '双引号', "'": '单引号'}


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


TTS_PATH = resource_path('tts.wav')
AUDIO_PATH = resource_path('audio.pcm')


class ChunJi:
    def __init__(self):
        self.find_result = []
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
        self.play_mode = 1
        self.judge_play()

        # noinspection PyBroadException
        try:
            with open('userconfig.json', 'r') as f:
                userconfig = json.load(f)
            self.listen_mode = userconfig['listen_mode']

        except:
            self.listen_mode = 1
            userconfig = {'listen_mode': self.listen_mode}
            with open('userconfig.json', 'w') as f:
                json.dump(userconfig, f)

        # keyboard.add_hotkey("alt", self.on_alt_press)
        keyboard.add_hotkey("space", self.on_space_press)

        self.welcome()

    def judge_play(self):
        if platform.system() == 'Darwin':
            try:
                from playsound import playsound
            except ImportError:
                self.play_mode = 1
            else:
                self.play_mode = 2
        else:
            self.play_mode = 1

    def welcome(self):
        self.no_file()
        self.speech("欢迎使用唇记,请先打开或新建文件")

    # def on_space_press(self):
    #     self.audio_record("space")
    #     self.result = eval(sasr())
    #     self.result_text = self.result["result"]["text"]
    #     if self.result["result"]["score"] < 0.6:
    #         self.speech("准确率低，建议检查")
    #     print(self.result)
    #     print(self.result_text)

    def on_space_press(self):
        if self.listen_mode == 1:
            self.audio_record("space")
            self.response_audio()

    def response_audio(self):
        self.result = eval(sasr())
        self.result_text = self.result["result"]["text"]
        print(self.result_text)
        if self.result["result"]["score"] < 0.5:
            print(self.result["result"]["score"])
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

            elif self.pending == '选择查找':
                self.choose_find()

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

        elif '纠错' in self.result_text or '检查' in self.result_text:
            self.ai_corrector_method()

        # elif self.result_text in ['移动', '移动光标']:
        #     self.move_cursor_method()

        elif '移动' in self.result_text or '光标' in self.result_text:
            self.move_cursor_method()

        elif '查' in self.result_text or '找' in self.result_text:
            self.find_method()

        elif '删' in self.result_text:
            self.delete_method()

        elif self.result_text in ['撤销', '撤回']:
            self.undo()

        elif self.result_text in ['重做', '取消撤回', '还原']:
            self.redo()

        elif self.result_text in ["保存", '存储']:
            self.save_file()

        elif '关闭' in self.result_text:
            self.close()

        elif '退出' in self.result_text:
            self.exit()

        elif '键盘' in self.result_text:
            self.keyboard_method()
        elif '智能' in self.result_text:
            self.smart_method()

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
                self.speech('插入标点:' + PUNC[self.result_text], go_smart_record=False)
            elif self.result_text == '空格':
                self.result_text = ' '
                self.speech('插入空格', go_smart_record=False)

            left = self.text[0:self.cursor]
            right = self.text[self.cursor:]
            self.cursor += len(self.result_text)
            self.text = left + self.result_text + right
            # self.saved = False
            if self.listen_mode == 2:
                self.smart_record()
            print(self.text)

    def keyboard_method(self):
        self.listen_mode = 1
        userconfig = {'listen_mode': self.listen_mode}
        with open('userconfig.json', 'w') as f:
            json.dump(userconfig, f)
        self.speech('已切换至键盘模式')

    def smart_method(self):
        self.listen_mode = 2
        userconfig = {'listen_mode': self.listen_mode}
        with open('userconfig.json', 'w') as f:
            json.dump(userconfig, f)
        self.speech('已切换至智能模式')

    def find_method(self):
        pattern = r'[查找搜索\s]'
        obj = re.sub(pattern, '', self.result_text)
        self.find_result = self.find_text(obj)
        if len(self.find_result) == 0:
            self.speech('未找到%s' % obj)
        else:
            self.pending = '选择查找'
            self.speech('查找%s，一共找到%d个结果，请选择要前往第几个' % (obj, len(self.find_result)))

    def choose_find(self):
        num = self.abstract_digit(self.result_text)
        if num != -1:
            self.log.append((self.text, self.cursor))
            self.cursor = self.find_result[num - 1]
            self.pending = ""
            self.speech('已移动到第%d个结果后' % num)

    def find_text(self, obj):
        find_result = [0]
        text = self.text
        while text.find(obj) != -1:
            cur = text.find(obj) + len(obj) + find_result[-1]
            find_result.append(cur)
            text = self.text[cur:]
        return find_result[1:]

    def move_cursor_method(self):
        # self.pending = '移动光标'

        # self.speech('请选择光标将移动的位置')

        if ('前' in self.result_text or '上' in self.result_text) and ('字' in self.result_text):
            if self.abstract_digit(self.result_text) != -1:
                self.log.append((self.text, self.cursor))
                self.cursor -= self.abstract_digit(self.result_text)
                if self.cursor < 0:
                    self.cursor = 0
                    self.speech('警告：超出文件范围，光标已移动至文档开头')
                else:
                    self.speech('光标已前移' + str(self.abstract_digit(self.result_text)) + '字')

        elif ('后' in self.result_text or '下' in self.result_text) and ('字' in self.result_text):
            if self.abstract_digit(self.result_text) != -1:
                self.log.append((self.text, self.cursor))
                self.cursor += self.abstract_digit(self.result_text)
                if self.cursor > len(self.text):
                    self.cursor = len(self.text)
                    self.speech('警告：超出文件范围，光标已移动至文档末尾')
                else:
                    self.speech('光标已后移' + str(self.abstract_digit(self.result_text)) + '字')

        elif ('前' in self.result_text or '上' in self.result_text or '首' in self.result_text) and (
                '句' in self.result_text):
            if self.cursor != 0:
                self.log.append((self.text, self.cursor))
                if self.text[self.cursor - 1] in PUNC.keys():
                    self.cursor -= 1
                while not self.text[self.cursor - 1] in PUNC.keys():
                    self.cursor -= 1
                self.speech('光标已移动至前一句')
            else:
                self.speech('光标已在文档开头')

        elif (
                '后' in self.result_text or '下' in self.result_text or '末' in self.result_text or
                '尾' in self.result_text) and ('句' in self.result_text):
            if self.cursor != len(self.text):
                self.log.append((self.text, self.cursor))
                if self.text[self.cursor - 1] in PUNC.keys():
                    self.cursor += 1
                while not self.text[self.cursor - 1] in PUNC.keys():
                    self.cursor += 1
                self.speech('光标已移动至后一句')
            else:
                self.speech('光标已在文档末尾')

        elif ('前' in self.result_text or '上' in self.result_text or '首' in self.result_text) and (
                '段' in self.result_text):
            if self.cursor != 0:
                self.log.append((self.text, self.cursor))
                if self.text[self.cursor - 1] == '\n':
                    self.cursor -= 1
                while not self.text[self.cursor - 1] == '\n':
                    self.cursor -= 1
                self.speech('光标已移动至前一段')
            else:
                self.speech('光标已在文档开头')

        elif (
                '后' in self.result_text or '下' in self.result_text or '末' in self.result_text
                or '尾' in self.result_text) and ('段' in self.result_text):
            if self.cursor != len(self.text):
                self.log.append((self.text, self.cursor))
                if self.text[self.cursor - 1] == '\n':
                    self.cursor += 1
                while not self.text[self.cursor - 1] == '\n':
                    self.cursor += 1
                self.speech('光标已移动至后一段')
            else:
                self.speech('光标已在文档末尾')

        elif '头' in self.result_text or '开' in self.result_text:
            self.log.append((self.text, self.cursor))
            self.cursor = 0
            self.speech('光标已移动至文档开头')

        elif '尾' in self.result_text or '末' in self.result_text:
            self.log.append((self.text, self.cursor))
            self.cursor = len(self.text)
            self.speech('光标已移动至文档末尾')

        else:
            self.speech('无法移动光标')

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
        self.pending = '朗读选择'
        self.speech('请选择要朗读的内容')

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

    def ai_corrector_method(self):
        if ('全文' in self.result_text) or ('所有' in self.result_text) or ('全' in self.result_text):
            self.check_content(self.selector('全文'))
        elif ('上一句' in self.result_text) or ('上句' in self.result_text) or ('前一句' in self.result_text) or (
                '前句' in self.result_text):
            self.check_content(self.selector('上一句'))
        elif ('下一句' in self.result_text) or ('下句' in self.result_text) or ('后一句' in self.result_text) or (
                '后句' in self.result_text):
            self.check_content(self.selector('下一句'))
        elif ('上一段' in self.result_text) or ('上段' in self.result_text) or ('前一段' in self.result_text) or (
                '前段' in self.result_text):
            self.check_content(self.selector('上一段'))
        elif ('下一段' in self.result_text) or ('下段' in self.result_text) or ('后一段' in self.result_text) or (
                '后段' in self.result_text):
            self.check_content(self.selector('下一段'))
        else:
            self.speech('无法检测内容')

    def check_content(self, content):
        if self.listen_mode == 1:
            self.speech('AI检查中')
        import pycorrector
        corrected_sent, detail = pycorrector.correct(content)
        print(corrected_sent, detail)
        if len(detail) == 0:
            self.speech('无智能纠错内容')
        else:
            speech_text = ''
            speech_text += '检测出' + str(len(detail)) + '个错误,'
            t = 1
            for i in detail:
                speech_text += '第' + str(t) + '个错误：' + i[0] + '应为' + i[1] + '。'
                t += 1
            # self.speech('请选择要改正的错误')
            # self.pending = '选择纠错'
            self.log.append((self.text, self.cursor))
            self.text = corrected_sent
            speech_text += '已纠错'
            self.speech(speech_text)

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
        if '无标点' in self.result_text:
            if content == '全文':
                self.speech(self.text)
            elif content == '上一句':
                self.speech(self.selector('上一句'))
            elif content == '下一句':
                self.speech(self.selector('下一句'))
            elif content == '上一段':
                self.speech(self.selector('上一段'))
            elif content == '下一段':
                self.speech(self.selector('下一段'))

        else:
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

    def delete_method(self):
        temp_cursor = self.cursor
        if ('前' in self.result_text or '上' in self.result_text) and ('字' in self.result_text):
            if self.abstract_digit(self.result_text) != -1:
                self.log.append((self.text, self.cursor))
                temp_cursor -= self.abstract_digit(self.result_text)
                if temp_cursor < 0:
                    temp_cursor = 0
                    self.del_area(temp_cursor, self.cursor)
                    self.speech('警告：超出文件范围，删除至文档开头')
                else:
                    self.del_area(temp_cursor, self.cursor)
                    self.speech('已删除前' + str(self.abstract_digit(self.result_text)) + '字')

        elif ('后' in self.result_text or '下' in self.result_text) and ('字' in self.result_text):
            if self.abstract_digit(self.result_text) != -1:
                self.log.append((self.text, self.cursor))
                temp_cursor += self.abstract_digit(self.result_text)
                if temp_cursor > len(self.text):
                    temp_cursor = len(self.text)
                    self.del_area(temp_cursor, self.cursor)
                    self.speech('警告：超出文件范围，删除至文档末尾')
                else:
                    self.del_area(temp_cursor, self.cursor)
                    self.speech('已删除后' + str(self.abstract_digit(self.result_text)) + '字')

        elif ('前' in self.result_text or '上' in self.result_text or '首' in self.result_text) and (
                '句' in self.result_text):
            if temp_cursor != 0:
                self.log.append((self.text, self.cursor))
                if self.text[temp_cursor - 1] in PUNC.keys():
                    temp_cursor -= 1
                while not self.text[temp_cursor - 1] in PUNC.keys():
                    temp_cursor -= 1
                self.del_area(temp_cursor, self.cursor)
                self.speech('已删除前一句')
            else:
                self.del_area(temp_cursor, self.cursor)
                self.speech('光标在文档开头')

        elif (
                '后' in self.result_text or '下' in self.result_text or '末' in self.result_text or
                '尾' in self.result_text) and ('句' in self.result_text):
            if temp_cursor != len(self.text):
                self.log.append((self.text, self.cursor))
                if self.text[temp_cursor - 1] in PUNC.keys():
                    temp_cursor += 1
                while not self.text[temp_cursor - 1] in PUNC.keys():
                    temp_cursor += 1
                self.del_area(temp_cursor, self.cursor)
                self.speech('已删除后一句')
            else:
                self.del_area(temp_cursor, self.cursor)
                self.speech('光标在文档末尾')

        elif ('前' in self.result_text or '上' in self.result_text or '首' in self.result_text) and (
                '段' in self.result_text):
            if temp_cursor != 0:
                self.log.append((self.text, self.cursor))
                if self.text[temp_cursor - 1] == '\n':
                    temp_cursor -= 1
                while not self.text[temp_cursor - 1] == '\n':
                    temp_cursor -= 1
                self.del_area(temp_cursor, self.cursor)
                self.speech('已删除前一段')
            else:
                self.del_area(temp_cursor, self.cursor)
                self.speech('光标在文档开头')

        elif (
                '后' in self.result_text or '下' in self.result_text or '末' in self.result_text
                or '尾' in self.result_text) and ('段' in self.result_text):
            if temp_cursor != len(self.text):
                self.log.append((self.text, self.cursor))
                if self.text[temp_cursor - 1] == '\n':
                    temp_cursor += 1
                while not self.text[temp_cursor - 1] == '\n':
                    temp_cursor += 1
                self.del_area(temp_cursor, self.cursor)
                self.speech('已删除后一段')
            else:
                self.del_area(temp_cursor, self.cursor)
                self.speech('光标已在文档末尾')
        else:
            self.speech('错误：无法识别删除内容')

    def del_area(self, start, end):
        if start > end:
            start = start + end
            end = start - end
            start = start - end
        self.text = self.text[:start] + self.text[end:]
        self.cursor = start

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
            right = self.text[self.cursor:]
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
            right = self.text[self.cursor:]
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
        if (self.text != self.previous_saved) and (not ('强制' in self.result_text)):
            self.speech('警告：当前文件未保存,使用强制退出以放弃更改')
        else:
            if self.listen_mode == 1:
                self.speech('欢迎下次使用', block=True)
            sys.exit()

    def close(self):
        if (self.text != self.previous_saved) and (not ('强制' in self.result_text)):
            self.speech('警告：当前文件未保存,使用强制关闭以放弃更改')
        else:
            # self.listen_method = 1
            self.find_result = []
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

            # self.__init__()

            self.pending = "打开或新建"
            self.speech('已关闭，请打开或新建文件')

    def response_file(self):
        if "打开" in self.result_text:
            self.pending = ""
            self.open_file()

        elif "新建" in self.result_text or "兴建" in self.result_text:
            self.pending = ""
            self.new_file()

        else:
            self.speech("错误，请选择打开或新建")

    def new_file(self):
        self.pending = "命名"
        self.speech("请命名")

    def new_name(self):
        self.unconfirmed_name = self.result_text + ".txt"
        self.pending = "命名确认"
        self.speech("将命名为：" + self.unconfirmed_name + "。确认请说：'是'", filename=True)

    def confirm_name(self):
        if self.result_text in ['是', '确认', '是的']:
            self.name = self.unconfirmed_name
            self.have_file = True
            self.pending = ""
            self.log.append((self.text, self.cursor))
            # self.saved = False
            self.speech("新建成功。当前模式：控制")
        else:
            self.pending = "命名"
            self.speech('请重新说出文件名')

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
            self.pending = "选文件"
            print(self.open_list)
            self.speech(self.read_file_tts, filename=True)

    def choose_file(self):
        # try:
        self.result_text = self.abstract_digit(self.result_text)
        if self.result_text != -1:
            index = int(self.result_text) - 1
            # except ValueError:
            #     self.speech("请说数字")
            # else:
            try:
                self.name = self.open_list[index]
            except IndexError:
                self.speech('数字错误')
            else:
                with open(self.name, "r") as f:
                    self.text = f.read()

                self.pending = ""
                self.have_file = True
                self.cursor = len(self.text)
                self.previous_saved = self.text
                self.log.append((self.text, self.cursor))
                self.speech('已打开文件:' + self.name + '。当前模式：控制', filename=True)

    def smart_record(self):
        self.play_audio(resource_path(os.path.join('bin', 'beep.wav')), block=True)
        if self.listen_mode == 2:
            CHUNK = 4096
            FORMAT = pyaudio.paInt16  # 16bit编码格式
            CHANNELS = 1  # 单声道
            RATE = 16000  # 16000采样频率

            VOLUME_THRESHOLD = 1000
            MAX_SILENCE_CHUNK = 1

            p = pyaudio.PyAudio()
            # 创建音频流
            stream = p.open(format=FORMAT,  # 音频流wav格式
                            channels=CHANNELS,  # 单声道
                            rate=RATE,  # 采样率16000
                            input=True,
                            frames_per_buffer=CHUNK)

            print("开始录制...")

            frames = []  # 录制的音频流

            startRec = False
            silentChunk = 0

            while True:
                try:
                    data = stream.read(CHUNK)
                except Exception as e:
                    print('error')
                    print(e)
                    continue
                npdata = np.frombuffer(data, dtype=np.short)
                if max(npdata) > VOLUME_THRESHOLD:
                    startRec = True
                    silentChunk = 0
                    # print("**recording**")
                    frames.append(data)
                elif startRec:
                    silentChunk += 1
                    # print('...')
                    if silentChunk < 2:
                        frames.append(data)
                    elif silentChunk >= 2 + MAX_SILENCE_CHUNK:
                        frames.append(data)
                        break

                # startBuffer = []
                # if max(npdata) > VOLUME_THRESHOLD:
                #     if not startRec:
                #         # print("**recording**")
                #         # print('**',max(npdata),'**')
                #         startBuffer.append(data)
                #         if len(startBuffer) > 1:
                #             startRec = True
                #             frames += startBuffer
                #             startBuffer = []
                #     else:
                #         silentChunk = 0
                #         # print("**recording**")
                #         frames.append(data)
                # elif startRec:
                #     silentChunk += 1
                #     # print('...')
                #     if silentChunk < 2:
                #         frames.append(data)
                #     elif silentChunk >= 2 + MAX_SILENCE_CHUNK:
                #         frames.append(data)
                #         break

            # 录制完成
            stream.stop_stream()
            stream.close()
            p.terminate()

            print("录制完成...")

            # 保存音频文件
            wf = wave.open(AUDIO_PATH, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            self.response_audio()

    def audio_record(self, key):
        if self.listen_mode == 1:
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
            wf = wave.open(AUDIO_PATH, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

    def speech(self, text, block=False, filename=False, read_punc=False, go_smart_record=True):
        if filename:
            if "." in text:
                text = text.replace(".", "点")

        if read_punc:
            text = text.replace('    ', '空两格')
            text = text.replace(' ', ' 空格 ')
            for i in PUNC.keys():
                text = text.replace(i, ' ' + PUNC[i] + ' ')

        print(text)
        tts(text)
        if self.listen_mode == 1:
            self.play_audio(TTS_PATH, block=block)
        elif self.listen_mode == 2:
            self.play_audio(TTS_PATH, block=True)
            if go_smart_record:
                self.smart_record()

    def play_audio(self, path, block=False):
        if self.play_mode == 1:
            # define stream chunk
            chunk = 1024

            # open a wav format music
            f = wave.open(path, "rb")
            # instantiate PyAudio
            p = pyaudio.PyAudio()
            # open stream
            stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True)
            # read data
            data = f.readframes(chunk)

            # play stream
            while data:
                stream.write(data)
                data = f.readframes(chunk)

                # stop stream
            stream.stop_stream()
            stream.close()

            # close PyAudio
            p.terminate()
        elif self.play_mode == 2:
            from playsound import playsound
            playsound(path, block=block)

    def abstract_digit(self, text):
        import chinese2digits as c2d
        text = text.replace('啊', '二')
        text = text.replace('两', '二')
        try:
            num = int(c2d.takeNumberFromString(text)['digitsStringList'][0])
        except IndexError:
            self.speech('警告：未检测到数字')
            return -1
        else:
            return num


if __name__ == "__main__":
    chunji = ChunJi()
    keyboard.wait("esc")
