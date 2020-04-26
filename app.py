from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import numpy as np
import pandas as pd
from googletrans import Translator
import sys
import datetime
import pygsheets


app = Flask(__name__)

# LINE 聊天機器人的基本資料
# # Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
# Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')

GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1O1aZsPhihNoG1fF_H1vj59ZLB_Dve7sgwcsGoRj3oh0/edit#gid=0'
sh = gc.open_by_url(survey_url)
ws = sh.sheet1
# 讀取單一儲存格值
val = ws.get_value('A1')
print(val)
# 以dataframe形式讀取資料
user_df = ws.get_as_df(start='A1', index_colum=0, empty_value='', include_tailing_empty=False,numerize=False) # index 從 0 開始算
print(user_df)


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

#取得第一次交談時的歡迎詞
#welcomeStr=getWelcomeStr()
#users=[]
#defaultFuncNum=1

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    if event.message.type== 'text':
        #if user_id is None:
        #    user_id = event.source.user_id
        #    print("user_id =", user_id)
        

        #ws2 = sh.sheet2
        # 輸出
        #ws.export(filename='df')
        # 讀取
        #df3 = pd.read_csv('df.csv')
        #print("df=",df3)

        #if (df3==None):
        #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='No data found.'))
        #    print('No data found.')
        #else: 
        #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='要問的問題已下載完畢！'))
        #    print('要問的問題已下載完畢！')
        
        line_bot_api.reply_message(event.reply_token, text='hi.')
    print("=======Reply Token=======")
    print(event.reply_token)
    print("=========================")

def question():
    gc = pygsheets.authorize(service_account_file='question.json')
    survey_url = 'https://docs.google.com/spreadsheets/d/1O1aZsPhihNoG1fF_H1vj59ZLB_Dve7sgwcsGoRj3oh0/edit#gid=0'
    sh = gc.open_by_url(survey_url)
    ws = sh.sheet1
    ws.update_value('A1', 'test')

def translate(event):
    translator = Translator()
    lang = translator.detect(event.message.text)
    print("Lang=",lang.lang)
    if event.message.type == 'text':
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

def getWelcomeStr():
    myResult='您好，歡迎來到資策會英文小教室。輸入數字切換功能：\n輸入1：翻譯小達人\n輸入2：出題小老師\n輸入？：列出設定指令'
    
    #return myResult

def setFunction(FuncNum,event):
    defaultFuncNum=FuncNum
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=''))
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
