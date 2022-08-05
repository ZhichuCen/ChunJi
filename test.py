# import wave
# import pyaudio
# from sasr import sasr
# import keyboard
#
#
# # 用Pyaudio库录制音频
# #   out_file:输出音频文件名
# #   rec_time:音频录制时间(秒)
# def audio_record(out_file, rec_time):
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16  # 16bit编码格式
#     CHANNELS = 1  # 单声道
#     RATE = 16000  # 16000采样频率
#
#     p = pyaudio.PyAudio()
#     # 创建音频流
#     stream = p.open(format=FORMAT,  # 音频流wav格式
#                     channels=CHANNELS,  # 单声道
#                     rate=RATE,  # 采样率16000
#                     input=True,
#                     frames_per_buffer=CHUNK)
#
#     print("Start Recording...")
#
#     frames = []  # 录制的音频流
#     # 录制音频数据
#     for i in range(0, int(RATE / CHUNK * rec_time)):
#         data = stream.read(CHUNK)
#         frames.append(data)
#
#     # 录制完成
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#
#     print("Recording Done...")
#
#     # 保存音频文件
#     wf = wave.open(out_file, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()
#
#
# # audio_record('audio.pcm', 5)
# # sasr()
#
# def on_keyboard_response():
#     print('hh')
#
#
# if __name__ == '__main__':
#     keyboard.add_hotkey('sapce or alt', on_keyboard_response)
#     # 按f1输出aaa
#     keyboard.wait('esc')
#     # wait里也可以设置按键，说明当按到该键时结束

# t = 'abcdefg'
# print(t[2::])
# import os

# print(os.listdir())

# t = '无12'
# print(int(t))

# import chinese2digits as c2d
#
# #混合提取
# print(c2d.takeNumberFromString('我123一二三')['replacedText'])

text = "abc.txt"
if "." in text:
    text = text.replace(".", "点")
print(text)

