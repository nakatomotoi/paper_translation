# Flaskのインポート
from flask import Flask
app = Flask(__name__)

import os
# OCRを行うtesserocr関連のライブラリをインポート
import tesserocr
from tesserocr import PyTessBaseAPI, PSM
# pdfをpngに変えるconvert_from_pathをインポート
from pdf2image import convert_from_path, convert_from_bytes

# pybitflyer:pythonからAPIを使えるように
from pybitflyer import API
# APIキーダウンロードのためのconfig.pyからConfig classをインポート
from config import Config
# APIキーリクエストのためのjsonファイルをインポート・リクエストできるライブラリのインポート
import sys
import json
import requests

# テキストデータの行を文字数ごとに折り返すライブラリ
import textwrap
# テキストデータをpdfに書き出すライブラリ
from reportlab.pdfgen import canvas
# pdfデータの編集ライブラリ
from reportlab.pdfbase import pdfmetrics
# 日本語のフォントに使えるフォント
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from PIL import Image, ImageFilter


# 実行ファイルと同じディレクトリにあるsample1.pdfをpdf2imageでpngに変換する
path = os.path.join(os.path.dirname(__file__), 'sample1.pdf')
images = convert_from_path(path)
# pngファイルをTesserocrでテキストデータに変換し、text_listに格納
text_list = ['a'] *len(images)
text_translated = ['b'] * len(images)
for i in range(len(images)):
    images[i].save('test{}.png'.format(i), 'png')
    api = PyTessBaseAPI(psm=PSM.AUTO, lang='eng')
    api.SetImageFile('test{}.png'.format(i))
    text_list[i] = api.GetUTF8Text()

# config.jsonに格納されているAPIキーを使用可能に
path_json= os.path.join(os.path.dirname(__file__), "config.json")
api = Config(path_json)
api_key = api.api_key

key = "?key=" + api_key
url = "https://translation.googleapis.com/language/translate/v2"
language = "&source=en&target=ja"
# google translationでtext_listのテキストデータを日本語へ翻訳し、text_translatedにページごとに格納
for i in range(len(images)):
    q = "&q=" + text_list[i]
    url_a = url + key + q + language
    rr = requests.get(url_a)
    unit_aa = json.loads(rr.text)
    if "data" in unit_aa:
        result = unit_aa['data']['translations'][0]['translatedText']
    else:
        result = "このページでは翻訳エラーが発生しました"
    text_translated[i] = result

# 日本語のフォントの決定
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
# 翻訳後のpdfファイルのタイトル作成
c = canvas.Canvas("test.pdf")
# text_translatedからtest.pdfに書き込み・表示
for j in range(len(text_translated)):
    text_case = textwrap.wrap(text_translated[j], 50)
    c.setFont('HeiseiMin-W3', 10.5)
    for i in range(len(text_case)):
        c.drawString(10, 830 - i * 12, text_case[i])
    c.showPage()
c.save()

# pdfを表示用にpngにする（pngファイルはバラバラ）
path_test = os.path.join(os.path.dirname(__file__), 'test.pdf')
result_images = convert_from_path(path_test)
for i in range(len(result_images)):
    result_images[i].save('result{}.png'.format(i), 'png')
    imgs = Image.open('result{}.png'.format(i))
#　結果の画像（pngファイル）を連結させて開く
def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

if len(result_images) > 2:
    combined = get_concat_v(Image.open('result0.png'), Image.open('result1.png'))
    combined.save('combined0.png')
    for j in range(len(result_images)-2):
        combined = get_concat_v(Image.open('combined{}.png'.format(j)), Image.open('result{}.png'.format(j+2)))
        combined.save('combined{}.png'.format(j+1))
    Image.open('combined{}.png'.format(len(result_images)-2)).show()
elif len(result_images) == 2:
    combined = get_concat_v(Image.open('result0.png'), Image.open('result1.png'))
    combined.save('combined0.png')
    Image.open('combined0.png').show()
else:
    IMage.open('result0.png').show()

if __name__ == "__main__":
    app.run(debug=False)
    