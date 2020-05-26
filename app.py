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
#users = np.array(('0','0',0)) #userID,level,point

##出題小老師  初始抓資料＆資料處理------------------------------------------------
level = 1 #預設level 1
isAsked = False
isSettingLevel = False
isChangingLevel = True
index = 0
GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1Zf5Qr_dp5GjYZJbxuVKl283fIRKUgs2q9nYNBeTWKJ8/edit#gid=0'
sh = gc.open_by_url(survey_url)

#取得所有工作表名稱
worksheet_list = sh.worksheets()
print("worksheet_list",worksheet_list)
ws1 = worksheet_list[0]
ws2 = worksheet_list[1]
ws3 = worksheet_list[2]

ws1.export(filename='df1') 
ws2.export(filename='df2') 
ws3.export(filename='df3') 
data1 = pd.read_csv('df1.csv') #type: <class 'pandas.core.frame.DataFrame'>
data2 = pd.read_csv('df2.csv')
data3 = pd.read_csv('df3.csv')


def getSheet():  #打亂該sheet順序，並存成dictionary格式  
    if(level == 3):
        data = data3
    elif(level == 2):
        data = data2
    else:
        data = data1

    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
    #df = np.random.sample(data)
    print("getSheet df = ",df)
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
            myResult = setLevel("N")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
        elif (replytext =='?'):
            isAsked = False
            myResult = setLevel("N")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
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

    if(isSettingLevel==True):
        levelinput = event.postback.data
        myResult = setLevel(levelinput) 
        print("myResult",myResult)
        if myResult == 'N' :
            print("level setting")
            levelButton(event)
        else:
            print("level change")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
    else:    
        print("correct answer = ",str(sheet["answer"][index]))
        print("index = ", index)
        answer = event.postback.data
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
def setLevel(levelinput):
    print("---Changing Level---")
    global data
    global sheet
    global qNum
    global level
    global isChangingLevel
    global isAsked
    global isSettingLevel
    #levelinput = event.message.text
    if (levelinput=='L'):
        level = 1
        isChangingLevel = False
        isSettingLevel = False
        myResult= ("目前程度切換至Level 1 初級 \n 請任意輸入 將開始出題～～")
        
    elif (levelinput=='M'):
        level = 2
        isChangingLevel = False
        isSettingLevel = False
        myResult= ("目前程度切換至Level 2 中級\n 請任意輸入 將開始出題～～")    
    elif (levelinput=='H'):
        level = 3
        isChangingLevel = False
        isSettingLevel = False
        myResult= ("目前程度切換至Level 3 高級\n 請任意輸入 將開始出題～～")  
    else:       
        isChangingLevel = True
        isSettingLevel = True
        #myResult="您好，歡迎來到資策會Line Bot 英文小老師～\n 請輸入以下指令切換題目程度：\n輸入1：初級\n輸入2：中級\n輸入3: 高級\n？：列出設定題目程度指令"
        myResult = "N"
    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
  
    print("myResult",myResult)    
    sheet,qNum = getSheet()
    
    print("level get sheet",sheet)
    print("level get qNum",qNum)
    return myResult

def levelButton(event):
    buttons_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '請選擇出題小老師題目程度～',
                        #text = question,
                        #thumbnail_image_url = '顯示在開頭的大圖片網址',
                        actions = [
                                PostbackTemplateAction(
                                    label = "初級", 
                                    text = "初",
                                    data = 'L'
                                ),
                                PostbackTemplateAction(
                                    label = "中級",
                                    text = "中",
                                    data = 'M'
                                ),
                                PostbackTemplateAction(
                                    label = "高級",
                                    text = "高",
                                    data = 'H'
                                )
                        ]
                    )
                )
    line_bot_api.reply_message(event.reply_token, buttons_template)  
    #return buttons_template
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
