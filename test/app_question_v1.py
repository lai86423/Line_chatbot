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

##出題小達人 
import sys 
import datetime 
import pygsheets 

app = Flask(__name__)

# LINE 聊天機器人的基本資料
# # Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
# Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')

#------------------------------------------
##出題小達人此處開始讀檔 初始參數

GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1O1aZsPhihNoG1fF_H1vj59ZLB_Dve7sgwcsGoRj3oh0/edit#gid=0'
sh = gc.open_by_url(survey_url)
ws = sh.sheet1
ws.export(filename='df')
df = pd.read_csv('df.csv')
#以dataframe形式讀取資料
#df = ws.get_as_df(index_colum=None, empty_value='', include_tailing_empty=False,numerize=False) # index 從 0 開始算
question = df.iloc[:,0]
optionA = df.iloc[:,1]
optionB = df.iloc[:,2]
optionC = df.iloc[:,3]
optionD = df.iloc[:,4]
feedback = df.iloc[:,5]
answer = df.iloc[:,6]
sheet = {
    "question": question,
    "optionA": optionA,
    "optionB": optionB,
    "optionC": optionC,
    "optionD": optionD,
    "feedback": feedback,
    "answer": answer
}
num = len(sheet["question"])
isAsked = False
index = 0

#----------------------------------------------------
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

#----------------------------------------------------
# 處理訊息
## 出題小達人功能
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked
    global index
    if event.message.type == 'text':
        if( isAsked == False ):            
            print(sheet["question"][index])
            print("1:", sheet["optionA"][index], "\n2:", sheet["optionB"][index], "\n3:", sheet["optionC"][index],
                    "\n4:", sheet["optionD"][index], "\n")

            option = ("1:" + sheet["optionA"][index] + "\n2:" + sheet["optionB"][index] + "\n3:" + 
                        sheet["optionC"][index] + "\n4:" + sheet["optionD"][index] + "\n")
            question = sheet["question"][index]
            ask = question + "\n" + option  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ask))  
            isAsked = True
            
        else:
            if(event.message.text != str(sheet["answer"][index])):
                feedback = sheet["feedback"][index]
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=feedback))
                isAsked = False
                index += 1
            else:
                print('答對了！你真棒！')
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='答對了！你真棒！'))
                isAsked = False
                index += 1
        
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

#-------------------------------------------------------
# def translate(event):
#     translator = Translator()
#     lang = translator.detect(event.message.text)
#     print("Lang=",lang.lang)
#     if event.message.type == 'text':
#         if lang.lang == "zh-CN" :
#             print("this is Chinese")
#             translateMessage = translator.translate(event.message.text, dest='en')
#             print(translateMessage.text)
#             message = TextSendMessage(text=translateMessage.text)
#         elif lang.lang =="en":
#             print("this is English")
#             translateMessage = translator.translate(event.message.text, dest='zh-tw')
#             print(translateMessage.text)
#             message = TextSendMessage(text=translateMessage.text)
#         else:
#             print("I can't translate this kind of message")
#             message = TextSendMessage(text="抱歉！機器人無法翻譯這種語言喔～")
#     else:
#         message = TextSendMessage(text="抱歉！機器人無法翻譯這種訊息呢～")
#     print("message=",message)
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
