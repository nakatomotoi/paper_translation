# Flaskのインポート
from flask import *
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

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

from flask_cors import CORS, cross_origin

from PIL import Image, ImageFilter

CORS(app, support_credentials=True)
@app.route('/')
def hello():
    return 'Hello Heroku_Flask'


@app.route('/translation', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def pdf_translation():
    print('ここ')
    if request.method == 'POST':
        print('うんち')
        filename = request.get_data()
        print(type(filename))
        print(convert_from_bytes)
        # 実行ファイルと同じディレクトリにあるsample1.pdfをpdf2imageでpngに変換する
        # path = os.path.join(os.path.dirname(__file__), filename)
        # convert_from_bytesを使うようにしました
        images = convert_from_bytes(filename)
        print(f'images: {images}')
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
        dict_list = [{'page_number': 1}]
        for i in range(len(images)-1):
            dict_list.append({'page_number': i+2})
        for i in range(len(images)):
            q = "&q=" + text_list[i]
            url_a = url + key + q + language
            rr = requests.get(url_a)
            unit_aa = json.loads(rr.text)
            print(f'unit_aa: {unit_aa}')
            text_translated[i] = unit_aa
            if 'data' in text_translated[i]:
                dict_list[i].update(translated_text=text_translated[i]['data']['translations'][0]['translatedText'])
            else:
                dict_list[i].update(translated_text="このページでは翻訳エラーが発生しました")

        dict_return = {}
        dict_return.update(data=dict_list)
        print(dict_return)
        return jsonify(dict_return)


"""
こんな感じのjsonが格納された配列が生成されている（pagenumberは1からスタート）
[{'data':{'translations':[{'translatedText':'Web工学'}]}'pagenumber':1}, 
{'data':{'translations':[{'translatedText':'深層学習'}]}, 'pagenumber':2}]
{'data': [{'page_number': int, 'translated_text': string}]}
"""
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
