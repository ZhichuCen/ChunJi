# -*- coding: utf-8 -*-

import os
import sys

import pygame

import urllib.request
import urllib.parse
import json
import re

url = 'http://www.braille.org.cn:8080/braille-web/braille/textToBraille.html'
if (os.path.exists('mangwen.txt')):
    os.remove('mangwen.txt')
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def toBraille(content):
    data = {}
    data['userId'] = '0'
    data['text'] = content
    data['firstLine'] = 'on'
    data['blankBefore'] = 'off'
    data['blankAfter'] = 'off'
    data['blankLine'] = 'off'
    data['shows'] = 'on'
    data['position'] = '1'
    data['format'] = '1'
    data['aligned'] = '1'
    data['pageLine'] = '32'
    data['show'] = '1'
    data['cnType'] = '1'
    data['enType'] = '1'
    data['rectNum'] = '32'
    data['breakLine'] = '1'
    data['flag'] = '2'

    data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')

    target = json.loads(html)
    target = target['info']['braille']
    target = target.split(
        '</td></tr></table><table  align="center"  style= "border-collapse:collapse"><tr><td style="text-align:center;font-size:32px">')
    translate = ''
    for word in target:
        translate = translate + word

    translate = translate.lstrip(
        '<p>1</p><table style= "margin-left:50px;"><tr><td style="text-align:left;font-size:32px"> ').rstrip(
        '</td></tr></table>')
    translate = re.sub('</td><td style="text-align:left;font-size:32px">', '', translate)
    translate = re.sub(
        '</td></tr></table><table style= "margin-left:50px;"><tr><td style="text-align:left;font-size:32px">', '',
        translate)
    translate = re.sub(
        '</td></tr></table><table style= "margin-left:50px;"><tr><td style="text-align:leftr;font-size:32px">', '',
        translate)
    # print(translate)
    # translate = translate.split('</td><td style="text-align:center;font-size:32px">')
    # translate = translate[2:]
    # translate[-1] = (translate[-1].split('</td>'))[0]
    mangwen = ''
    for word in translate:
        mangwen = mangwen + word

    print('对应的盲文是：%s' % (mangwen))

    pygame.init()
    font = pygame.font.Font(resource_path(os.path.join('bin', 'Apple Braille.ttf')), 35)
    rtext = font.render(mangwen, True, (0, 0, 0), (255, 255, 255))
    pygame.image.save(rtext, "text.jpg")

    with open("mangwen.txt", "a", encoding='utf-8') as f:
        f.write(mangwen + '\n')

    # text = mangwen
    # im = Image.new("RGB", (300, 50), (255, 255, 255))
    # dr = ImageDraw.Draw(im)
    # font = ImageFont.truetype(os.path.join("fonts", "Bold Six Dot Braille.otf"), 14)
    # dr.text((10, 5), text, font="Bold Six Dot Braille.otf", fill="#000000")
    # im.show()
    # im.save('output.png')


if __name__ == "__main__":
    toBraille('12345')
