# # import wave
# # import pyaudio
# # from sasr import sasr
# # import keyboard
# #
# #
# # # 用Pyaudio库录制音频
# # #   out_file:输出音频文件名
# # #   rec_time:音频录制时间(秒)
# # def audio_record(out_file, rec_time):
# #     CHUNK = 1024
# #     FORMAT = pyaudio.paInt16  # 16bit编码格式
# #     CHANNELS = 1  # 单声道
# #     RATE = 16000  # 16000采样频率
# #
# #     p = pyaudio.PyAudio()
# #     # 创建音频流
# #     stream = p.open(format=FORMAT,  # 音频流wav格式
# #                     channels=CHANNELS,  # 单声道
# #                     rate=RATE,  # 采样率16000
# #                     input=True,
# #                     frames_per_buffer=CHUNK)
# #
# #     print("Start Recording...")
# #
# #     frames = []  # 录制的音频流
# #     # 录制音频数据
# #     for i in range(0, int(RATE / CHUNK * rec_time)):
# #         data = stream.read(CHUNK)
# #         frames.append(data)
# #
# #     # 录制完成
# #     stream.stop_stream()
# #     stream.close()
# #     p.terminate()
# #
# #     print("Recording Done...")
# #
# #     # 保存音频文件
# #     wf = wave.open(out_file, 'wb')
# #     wf.setnchannels(CHANNELS)
# #     wf.setsampwidth(p.get_sample_size(FORMAT))
# #     wf.setframerate(RATE)
# #     wf.writeframes(b''.join(frames))
# #     wf.close()
# #
# #
# # # audio_record('audio.pcm', 5)
# # # sasr()
# #
# # def on_keyboard_response():
# #     print('hh')
# #
# #
# # if __name__ == '__main__':
# #     keyboard.add_hotkey('sapce or alt', on_keyboard_response)
# #     # 按f1输出aaa
# #     keyboard.wait('esc')
# #     # wait里也可以设置按键，说明当按到该键时结束
#
# # t = 'abcdefg'
# # print(t[2::])
# # import os
#
# # print(os.listdir())
#
# # t = '无12'
# # print(int(t))
#
# # import chinese2digits as c2d
# #
# # #混合提取
# # print(c2d.takeNumberFromString('我123一二三')['replacedText'])
#
# # text = "abc.txt"
# # if "." in text:
# #     text = text.replace(".", "点")
# # print(text)
#
# # print(len("你好哈哈"))
# # for i in range(4):
# #     print(i)
#
# with open('文档.txt', 'r') as f:
#     text = f.read()
# # # print('1\n'+text[37]+'\n1')
# # # t = '\n' == text[36]
# # # print(t)
# #
# # PUNC = {'。': '句号', '.': '点', '，': '逗号', ',': '逗号', '、': '顿号', '；': '分号', ';': '分号',
# #         '：': '冒号', ':': '冒号', '？': '问号', '?': '问号', '！': '感叹号', '!': '感叹号',
# #         '"': '引号', "'": '引号', '“': '引号', '”': '引号', '\n': '换行'}
# #
# #
# #
# # for i in PUNC.keys():
# #     text = text.replace(i, ' ' + PUNC[i] + ' ')
# #
# # print(text)
# #
# # text = text.replace('逗号', '，')
# #
# # print(text)
# # cursor = 55
# # print(text[cursor])
# #
# # print('left')
# # left = text[0:cursor]
# # print(left)
# # l = len(left)
# #
# # for i in range(l):
# #     t = left[-1 - i]
# #     if t in PUNC.keys() and i != 0:
# #         print(left[-i:])
# #         break
# #
# # print('right')
# #
# # right = text[cursor:-1]
# # print(right)
# # r = len(right)
# # for i in range(r):
# #     t = right[i]
# #     if t in PUNC.keys() and i != 0:
# #         print(right[:i+1])
# #         break
# # print(PUNC.values())
# #
# # result_text = '朗读'
# #
# # if '全文' or '所有' or '全' in result_text:
# #     print('yes')
#
# # PUNC = {'。': '句号', '，': '逗号', ',': '逗号', '、': '顿号', '；': '分号', ';': '分号',
# #         '：': '冒号', ':': '冒号', '？': '问号', '?': '问号', '！': '感叹号', '!': '感叹号',
# #         '"': '引号', "'": '引号', '“': '左引号', '”': '右引号', '\n': '换行',
# #         '（': '左括号', '）': '右括号', '(': '左括号', ')': '右括号',
# #         '——': '破折号', '—': '连接号', '-': '减号',
# #         '······': '省略号', '...': '省略号', '.': '点', '·': '间隔号', '《': '左书名号', '》': '右书名号'
# #         }
#
# # print(PUNC.keys())
# # print(PUNC.values())
#
# # PUNC_FULL = {'。': '句号', '，': '逗号', '、': '顿号', ';': '分号',
# #              '：': '冒号', '？': '问号', '！': '感叹号',
# #              '“': '左引号', '”': '右引号', '\n': '换行',
# #              '（': '左括号', '）': '右括号',
# #              '——': '破折号', '—': '连接号', '-': '减号',
# #              '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号'
# #              }
# #
# # PUNC_HALF = {'；': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号',
# #              '(': '左括号', ')': '右括号', '...': '省略号', '.': '点', '"': '双引号', "'": '单引号',
# #              }
# #
# # # print(dict(PUNC_FULL.items()+PUNC_HALF.items()))
# # print(dict(PUNC_FULL, **PUNC_HALF))
#
# def abstract_digit(text):
#     import chinese2digits as c2d
#     return c2d.takeNumberFromString(text)['digitsStringList']
# #
# txt = '移动前两个字'
# print(abstract_digit(txt))
# #
# # log = []
# # log.append(('ss',1))
# # print(log)
# # t,c = log.pop()
# # print(t,c)
# #
# # print('')
# # print(txt.replace('三','3',1))
#
#
# cursor = 20
# left = text[0:cursor]
# right = text[cursor:-1]
# print(left)
# print(right)
#
# print('')
#
# cursor_1 = 20
# left_1 = text[0:cursor_1]
# right_1 = text[cursor_1:-1]
# print(left_1)
# print(right_1)
#
# text = text[:cursor] + text[cursor_1:]
# print(text)
#
#
# a=55
# b=36
# a = a+b
# b = a-b
# a = a-b
# print(a,b)

# import pycorrector
# print('ready')
#
# corrected_sent, detail = pycorrector.correct('少先队员因该为老人让坐')
# # corrected_sent, detail = pycorrector.correct('少先队员应该为老人让座')
# print(corrected_sent, detail)

# x = [1,2]
# print(x[2])
# from playsound import playsound
#
# from tts import tts
#
#
# def speech(text, block=False, filename=False, read_punc=False):
#     # if filename:
#     #     if "." in text:
#     #         text = text.replace(".", "点")
#     #
#     # if read_punc:
#     #     text = text.replace(' ', '空格')
#     #     for i in PUNC.keys():
#     #         text = text.replace(i, ' ' + PUNC[i] + ' ')
#
#     print(text)
#     tts(text)
#     playsound("tts.wav", block=block)
#
#
# speech("欢迎使用唇记",block=True)
# import re
#
# with open('文档.txt', 'r') as f:
#     txt = f.read()
#
#
# # t = text.find('hhh')
# # print(t)
# # print(text[:t])
# # print(text[t:])
#
#
# # def find_text(obj, find_result=[], find_seq=0):
# #     t = text.find(obj)
# #     if t != -1:
# #         find_seq += (t + len(obj))
# #         find_result.append(find_seq)
# #         find_text(text[find_seq:], find_result=find_result, find_seq=find_seq)
# #     else:
# #         return find_result
#
#
# # def find_text(text, obj):
# #     find_result = [0]
# #     while text.find(obj) != -1:
# #         cur = text.find(obj) + len(obj) + find_result[-1]
# #         find_result.append(cur)
# #         text = txt[cur:]
# #     return find_result[1:]
# #
# #
# # print(find_text(txt, '乡'))
# result_text = '查找乡愁'
# pattern = r'[查找搜索\s]'
# obj = re.sub(pattern, '', result_text)
# print(obj,'\a')
#
#
# print('\a')
# import os
# print(os.path.splitext('文档1.txt'))
#
# data = ''
# print(data['str'])

message_log = [
        {"role": "system", "content": "You are a helpful assistant."},
{"role": "ass", "content": "16532"}
    ]
print(message_log[-1]["content"])

PUNC = {'。': '句号', '，': '逗号', '、': '顿号', ';': '分号', '：': '冒号', '？': '问号', '！': '感叹号', '    ': '空两格',
        '“': '左引号', '”': '右引号', '\n': '回车', '（': '左括号', '）': '右括号', '——': '破折号', '—': '连接号',
        '-': '减号',
        '······': '省略号', '·': '间隔号', '《': '左书名号', '》': '右书名号',
        '；': '分号', ',': '逗号', ':': '冒号', '?': '问号', '!': '感叹号', '(': '左括号', ')': '右括号',
        '...': '省略号', '.': '点', '"': '双引号', "'": '单引号'}

import string
s = "Hello,    world!。。？？——}{|、"
allpunc = "".join(PUNC.keys())+string.punctuation
table = str.maketrans("", "", allpunc)
s = s.translate(table)
print(s) # Hello world