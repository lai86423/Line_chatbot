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
ws.export(filename='df')
df = pd.read_csv('df.csv')
# 以dataframe形式讀取資料
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
            #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ask))  
            isAsked = True
            

            buttons_template = TemplateSendMessage (
                alt_text = 'Buttons Template',
                template = ButtonsTemplate(
                    title = '出題小老師',
                    text = question,
                    #thumbnail_image_url = '顯示在開頭的大圖片網址',
                    actions = [
                            PostbackTemplateAction(
                                label = ("(A) " + sheet["optionA"][index]), 
                                text = "(A)",
                                data = 'A'
                            ),
                            PostbackTemplateAction(
                                label = "(B) " + sheet["optionB"][index],
                                text = "(B)",
                                data = 'B'
                            ),
                            PostbackTemplateAction(
                                label = "(C) " + sheet["optionC"][index],
                                text = "(C)",
                                data = 'C'
                            ),
                            PostbackTemplateAction(
                                label = "(D) " + sheet["optionD"][index],
                                text = "(D)",
                                data = 'D'
                            )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, buttons_template)
            
        # else:
        #     if(event.message.text != str(sheet["answer"][index])):
        #         feedback = sheet["feedback"][index]
        #         line_bot_api.reply_message(event.reply_token, TextSendMessage(text=feedback))
        #         isAsked = False
        #         index += 1
        #     else:
        #         print('答對了！你真棒！')
        #         line_bot_api.reply_message(event.reply_token, TextSendMessage(text='答對了！你真棒！'))
        #         isAsked = False
        #         index += 1
        
        #if user_id is None:
        #    user_id = event.source.user_id
        #    print("user_id =", user_id)       

        #if (df3==None):
        #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='No data found.'))
        #    print('No data found.')
        #else: 
        #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='要問的問題已下載完畢！'))
        #    print('要問的問題已下載完畢！')
        
        #line_bot_api.reply_message(event.reply_token, text='hi.')
    print("=======Reply Token=======")
    print(event.reply_token)
    print("=========================")
    
@handler.add(PostbackEvent)
def handle_postback(event):
    global isAsked
    global index
    print("isAsked = ", isAsked)
    print("index = ", index)
    answer = event.postback.data
    print("postback(answer) = ", answer)
    if(answer != str(sheet["answer"][index])):
        feedback = sheet["feedback"][index]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
        isAsked = False
        index += 1
    else:
        print('答對了！你真棒！')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '答對了！你真棒！'))
        isAsked = False
        index += 1

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
