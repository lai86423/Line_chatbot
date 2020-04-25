from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from googletrans import Translator

import sys
import datetime

import pygsheets
gc = pygsheets.authorize(service_file='question.json')
import pygsheets

app = Flask(__name__)

# LINE 聊天機器人的基本資料
# # Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
# Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')

GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    gc = pygsheets.authorize(service_account_file='question.json')
    survey_url = 'https://docs.google.com/spreadsheets/d/1O1aZsPhihNoG1fF_H1vj59ZLB_Dve7sgwcsGoRj3oh0/edit#gid=0'
    sh = gc.open_by_url(survey_url)

    # Update a single cell.
    #ws.update_value('A1', "Numbers on Stuff")
    ws = sh.sheet1
    ws.update_value('A1', 'test')
    # Update the worksheet with the numpy array values. Beginning at cell 'A2'.
    #ws.update_values('A2', my_numpy_array.to_list())

    translator = Translator()
    if event.message.type == 'text':
        lang = translator.detect(event.message.text)
        print("Lang=",lang.lang)
        if lang.lang == "zh-CN" :
            print("this is Chinese")
            translateMessage = translator.translate(event.message.text, dest='en')
            print(translateMessage.text)
            message = TextSendMessage(text=translateMessage.text)
        elif lang.lang =="en":
            print("this is English")
            translateMessage = translator.translate(event.message.text, dest='zh-tw')
            print(translateMessage.text)
            message = TextSendMessage(text=translateMessage.text)
        else:
            print("I can't translate this kind of message")
            message = TextSendMessage(text="抱歉！機器人無法翻譯這種語言喔～")
    else:
        message = TextSendMessage(text="抱歉！機器人無法翻譯這種訊息呢～")
    print("message=",message)
    #print("event-----",event)
    line_bot_api.reply_message(event.reply_token, message)


    print("=======Reply Token=======")
    print(event.reply_token)
    print("=========================")

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
