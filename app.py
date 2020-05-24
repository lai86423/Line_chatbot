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

##出題小老師  import-----------------------------------------------
import sys
import datetime
import pygsheets

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')

##出題小老師  初始抓資料＆資料處理------------------------------------------------
#users = np.array(('0','0',0)) #userID,level,point
level = 0
isAsked = False
isChangingLevel = True
index = 0
GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1Zf5Qr_dp5GjYZJbxuVKl283fIRKUgs2q9nYNBeTWKJ8/edit#gid=0'
sh = gc.open_by_url(survey_url)

def getData(level): #先把該level google sheet存下來
    ws = sh.sheet1
    ws.export(filename='df') #先把google sheet存下來
    data = pd.read_csv('df.csv') #type: <class 'pandas.core.frame.DataFrame'>
    return data
def getSheet():  #打亂該sheet順序，並存成dictionary格式  
    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
    #df = np.random.sample(data)
    print("df = ",df)
    question = df.iloc[:,0]
    option1 = df.iloc[:,1]
    option2 = df.iloc[:,2]
    option3 = df.iloc[:,3]
    option4 = df.iloc[:,4]
    feedback = df.iloc[:,5]
    answer = df.iloc[:,6]
    sheet = {
        "question": question,
        "option1": option1,
        "option2": option2,
        "option3": option3,
        "option4": option4,
        "feedback": feedback,
        "answer": answer
    }
    qNum = len(sheet["question"])
    #print("df = ",df)
    #print("num = ",qNum)
    return sheet,qNum

data = getData(level)
sheet,qNum = getSheet()
##------------------------------------------------

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

##出題小老師  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked
    global index
    replytext = event.message.text
    #myId = event.source.user_id
    if event.message.type == 'text':   
        if (isChangingLevel == True):   
            setLevel(event)
        elif (replytext =='?'):
            isAsked = False
            setLevel(event)
        else:
            if( isAsked == False ):     
                print(sheet["question"][index])
                print("1:", sheet["option1"][index], "\n2:", sheet["option2"][index], "\n3:", sheet["option3"][index],
                        "\n4:", sheet["option4"][index], "\n")

                option = ("1:" + sheet["option1"][index] + "\n2:" + sheet["option2"][index] + "\n3:" + 
                            sheet["option3"][index] + "\n4:" + sheet["option4"][index] + "\n")
                question = sheet["question"][index]
                ask = question + "\n" + option  
                isAsked = True
                
                buttons_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '出題小老師',
                        text = question,
                        #thumbnail_image_url = '顯示在開頭的大圖片網址',
                        actions = [
                                PostbackTemplateAction(
                                    label = ("(1) " + sheet["option1"][index]), 
                                    text = "(1)",
                                    data = '1'
                                ),
                                PostbackTemplateAction(
                                    label = "(2) " + sheet["option2"][index],
                                    text = "(2)",
                                    data = '2'
                                ),
                                PostbackTemplateAction(
                                    label = "(3) " + sheet["option3"][index],
                                    text = "(3)",
                                    data = '3'
                                ),
                                PostbackTemplateAction(
                                    label = "(4) " + sheet["option4"][index],
                                    text = "(4)",
                                    data = '4'
                                )
                        ]
                    )
                )
                line_bot_api.reply_message(event.reply_token, buttons_template)   
    #print("=======Reply Token=======")
    #print(event.reply_token)
    #print("=========================")

##出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked
    global index
    global sheet
    global qNum
    print("correct answer = ",str(sheet["answer"][index]))
    print("index = ", index)
    answer = event.postback.data
    #print("postback(answer) = ", answer)
    if answer != str(sheet["answer"][index]):
        feedback = sheet["feedback"][index]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
        isAsked = False       
    else:
        print('答對了！你真棒！')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '答對了！你真棒！'))
        isAsked = False

    if index < qNum - 1:
        index += 1
    else:
        index = 0
        sheet,qNum = getSheet()
        print("new sheet",sheet)
        print("new qNum",qNum)
    print("index after = ", index)

##出題小老師  設定Level------------------------------------------------
def setLevel(event):
    print("---Changing Level---")
    global data
    global sheet
    global qNum
    global level
    global isChangingLevel
    global isAsked
    levelinput = event.message.text
    if (levelinput=='1'):
        level = 1
        isChangingLevel = False
        myResult= ("目前程度切換至Level 1 初級 \n 請任意輸入 將開始出題～～")
    elif (levelinput=='2'):
        level = 2
        isChangingLevel = False
        myResult= ("目前程度切換至Level 2 中級\n 請任意輸入 將開始出題～～")    
    elif (levelinput=='3'):
        level = 3
        isChangingLevel = False
        myResult= ("目前程度切換至Level 3 高級\n 請任意輸入 將開始出題～～")  
    else:       
        isChangingLevel = True
        myResult="您好，歡迎來到資策會Line Bot 英文小老師～\n 請輸入以下指令切換題目程度：\n輸入1：初級\n輸入2：中級\n輸入3: 高級\n？：列出設定題目程度指令"
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
    print(myResult)    
    
    data = getData(level)
    sheet,qNum = getSheet()
    print("sheet",sheet)
    print("qNum",qNum)

##出題小老師  End------------------------------------------------

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
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
