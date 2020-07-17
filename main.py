# Flaskのインポート
from flask import Flask
app = Flask(__name__)

import os
# OCRを行うtesseract関連のライブラリをインポート
import pyocr
import pyocr.builders
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


from PIL import Image, ImageFilter
@app.route('/')
def hello():
    return 'Hello Heroku_Flask'


@app.route('/translation')
def pdf_translation(filename):
    # 実行ファイルと同じディレクトリにあるsample1.pdfをpdf2imageでpngに変換する
    # path = os.path.join(os.path.dirname(__file__), filename)
    # convert_from_bytesを使うようにしました
    images = convert_from_bytes(open(filename, 'rb').read())
    # pngファイルをTesserocrでテキストデータに変換し、text_listに格納
    text_list = ['a'] * len(images)
    text_translated = ['b'] * len(images)
    for i in range(len(images)):
        tools = pyocr.get_available_tools()
        tool = tools[0]
        images[i].save('test{}.png'.format(i), 'png')
        text_list[i] = tool.image_to_string(
            Image.open(r'test{}.png'.format(i)),
            lang="eng",
            builder=pyocr.builders.TextBuilder()
        )

    # config.jsonに格納されているAPIキーを使用可能に
    path_json = os.path.join(os.path.dirname(__file__), "config.json")
    api = Config(path_json)
    api_key = api.api_key if api else os.environ["API_KEY"]

    key = "?key=" + api_key
    url = "https://translation.googleapis.com/language/translate/v2"
    language = "&source=en&target=ja"
    # google translationでtext_listのテキストデータを日本語へ翻訳し、text_translatedにページごとに格納
    dict_list= [{'page_number':1}]
    for i in range(len(images)-1):
        dict_list.append({'page_number':i+2})
    for i in range(len(images)):
        q = "&q=" + text_list[i]
        url_a = url + key + q + language
        rr = requests.get(url_a)
        unit_aa = json.loads(rr.text)
        text_translated[i] = unit_aa
        if 'data' in text_translated[i]:
            dict_list[i].update(translated_text=text_translated[i]['data']['translations'][0]['translatedText'])
        else:
            dict_list[i].update(translated_text="このページでは翻訳エラーが発生しました")

    dict_return = {}
    dict_return.update(data=dict_list)
    return dict_return


# pdf_translation(filename='sample1.pdf')
# print(pdf_translation(filename='sample1.pdf'))

"""
こんな感じのjsonが格納された配列が生成されている（pagenumberは1からスタート）
[{'data':{'translations':[{'translatedText':'Web工学'}]}'pagenumber':1}, 
{'data':{'translations':[{'translatedText':'深層学習'}]}, 'pagenumber':2}]
{'data': [{'page_number': int, 'translated_text': string}]}
"""
if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
