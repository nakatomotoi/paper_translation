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
@app.route('/')
def hello():
    return 'Hello Heroku_Flask'


def pdf_translation(filename):
# 実行ファイルと同じディレクトリにあるsample1.pdfをpdf2imageでpngに変換する
    path = os.path.join(os.path.dirname(__file__), filename)
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
        text_translated[i] = unit_aa
        text_translated[i].update(pagenumber=i+1)
    return text_translated

pdf_translation(filename='sample1.pdf')

"""
こんな感じのjsonが格納された配列が生成されている（pagenumberは1からスタート）
[{'data':{'translations':[{'translatedText':'Web工学'}]}'pagenumber':1}, 
{'data':{'translations':[{'translatedText':'深層学習'}]}, 'pagenumber':2}]
"""
if __name__ == "__main__":
    
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
    