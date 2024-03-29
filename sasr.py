# -*- coding: utf-8 -*-
import json
import os
import sys

from huaweicloud_sis.bean.asr_request import AsrCustomShortRequest
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.client.asr_client import AsrCustomizationClient
from huaweicloud_sis.utils import io_utils

# 鉴权参数
# 鉴权信息
ak = 'ZENS2IKKSHRU0VTY27YQ'  # 用户的ak
sk = 'Wpg1k1iQ2o9nPGEl0q1eq1DpMugQh7s0jcSKjJv3'  # 用户的sk
region = 'cn-east-3'  # region，如cn-north-4
project_id = 'a7b20cfec1f948dbb4a9d145456b21d7'  # 同region一一对应，参考https://support.huaweicloud.com/api-sis/sis_03_0008.html


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


AUDIO_PATH = resource_path('audio.pcm')

# 一句话识别参数
path = AUDIO_PATH  # 需要发送音频路径，如D:/test.pcm, 同时sdk也支持byte流发送数据。
path_audio_format = 'pcm16k16bit'  # 音频支持格式，如pcm16k16bit，详见api文档
path_property = 'chinese_16k_common'  # 属性字符串，language_sampleRate_domain, 如chinese_16k_common, 采样率要和音频一致。详见api文档

"""
    todo 请正确填写音频格式和模型属性字符串
    1. 音频格式一定要相匹配.
         例如wav音频，格式是wav。具体参考api文档。
         例如音频是pcm格式，并且采样率为8k，则格式填写pcm8k16bit。
         如果返回audio_format is invalid 说明该文件格式不支持。具体支持哪些音频格式，需要参考一些api文档。

    2. 音频采样率要与属性字符串的采样率要匹配。
         例如格式选择pcm16k16bit，属性字符串却选择chinese_8k_common, 则会返回'audio_format' is not match model
         例如wav本身是16k采样率，属性选择chinese_8k_common, 同样会返回'audio_format' is not match model
"""


# # 一句话识别参数，以音频文件的base64编码传入，1min以内音频
# path = ''  								# 文件位置, 需要具体到文件，如D:/test.wav
# path_audio_format = ''  				# 音频格式，如wav等，详见api文档
# path_property = 'chinese_16k_general'   # language_sampleRate_domain, 如chinese_16k_general，详见api文档


def sasr(detect_punc):
    """ 一句话识别示例 """
    # step1 初始化客户端
    config = SisConfig()
    config.set_connect_timeout(10)  # 设置连接超时
    config.set_read_timeout(10)  # 设置读取超时
    # 设置代理，使用代理前一定要确保代理可用。 代理格式可为[host, port] 或 [host, port, username, password]
    # config.set_proxy(proxy)
    asr_client = AsrCustomizationClient(ak, sk, region, project_id, sis_config=config)

    # step2 构造请求
    data = io_utils.encode_file(path)
    asr_request = AsrCustomShortRequest(path_audio_format, path_property, data)
    # 所有参数均可不设置，使用默认值
    # 设置是否添加标点，yes or no，默认no
    if detect_punc:
        asr_request.set_add_punc('yes')
    else:
        asr_request.set_add_punc('no')
    # 设置是否将语音中数字转写为阿拉伯数字，yes or no，默认yes
    asr_request.set_digit_norm('no')
    # 设置是否添加热词表id，没有则不填
    # asr_request.set_vocabulary_id(None)
    # 设置是否需要word_info，yes or no, 默认no
    asr_request.set_need_word_info('no')

    # step3 发送请求，返回结果,返回结果为json格式
    result = asr_client.get_short_response(asr_request)
    return json.dumps(result, indent=2, ensure_ascii=False)

# if __name__ == '__main__':
#     try:
#         sasr()
#     except ClientException as e:
#         print(e)
#     except ServerException as e:
#         print(e)
