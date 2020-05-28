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

##聽力測驗  import-----------------------------------------------
import sys
import datetime
import pygsheets

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level_L,point

##聽力  初始抓資料＆資料處理------------------------------------------------
level_L = 1 #預設level 1
isAsked_L = False
isChangingLevel_L = True
index_L = 0
GDriveJSON = 'question.json'
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url_L = 'https://docs.google.com/spreadsheets/d/1e1hCM0yFzwQkzfdzJGCioLCvnPNJHw9IPHqz4sSEsjg/edit#gid=0'
sh_L = gc.open_by_url(survey_url_L)

#取得所有工作表名稱
worksheet_list_L = sh_L.worksheets()
print("worksheet_list_L",worksheet_list_L)
ws1_L = worksheet_list_L[0]
ws2_L = worksheet_list_L[1]
ws3_L = worksheet_list_L[2]

ws1_L.export(filename='df1_L') 
ws2_L.export(filename='df2_L') 
ws3_L.export(filename='df3_L') 
data1_L = pd.read_csv('df1_L.csv') #type: <class 'pandas.core.frame.DataFrame'>
data2_L = pd.read_csv('df2_L.csv')
data3_L = pd.read_csv('df3_L.csv')

def getSheet(Qlevel):  #TODO 傳變數level,判斷是聽力還是出題小老師 #打亂該sheet順序，並存成dictionary格式  
    if(Qlevel == 3):
        data = data3_L
    elif(Qlevel == 2):
        data = data2_L
    else:
        data = data1_L

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
    return sheet,qNum

sheet,qNum = getSheet(level_L)
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

##聽力測驗  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked_L
    global index_L
    global isChangingLevel_L
    replytext = event.message.text
    #myId = event.source.user_id
    if event.message.type == 'text':   
        if (isChangingLevel_L == True or replytext =='?'):   
            isChangingLevel_L = True
            isAsked_L = False
            buttons_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '歡迎來到資策會LineBot聽力測驗！',
                        text = '請點選題目程度~',
                        actions = [
                                PostbackTemplateAction(
                                    label = "初級", 
                                    text = "初級",
                                    data = 'L'
                                ),
                                PostbackTemplateAction(
                                    label = "中級",
                                    text = "中級",
                                    data = 'M'
                                ),
                                PostbackTemplateAction(
                                    label = "高級",
                                    text = "高級",
                                    data = 'H'
                                )
                        ]
                    )
                )
            line_bot_api.reply_message(event.reply_token, buttons_template)  
        else:
            if( isAsked_L == False ):     
                print(sheet["question"][index_L])
                print("1:", sheet["option1"][index_L], "\n2:", sheet["option2"][index_L], "\n3:", sheet["option3"][index_L],
                        "\n4:", sheet["option4"][index_L], "\n")
                question = sheet["question"][index_L]
                isAsked_L = True
                
                buttons_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '聽力測驗',
                        text = question,
                        thumbnail_image_url='https://upload.cc/i1/2020/05/27/Hdyx42.jpg',
                        default_action = {
                            #type = 'uri',
                            "type": "uri",
                            "label": "View detail",
                            "uri": "https://developers.line.biz/en/reference/messaging-api/#buttons"
                            #uri = "https://developers.line.biz/en/reference/messaging-api/#buttons"
                        },
                        actions = [
                                PostbackTemplateAction(
                                    label = ("(1) " + sheet["option1"][index_L]), 
                                    text = "(1)",
                                    data = '1'
                                ),
                                PostbackTemplateAction(
                                    label = "(2) " + sheet["option2"][index_L],
                                    text = "(2)",
                                    data = '2'
                                ),
                                PostbackTemplateAction(
                                    label = "(3) " + sheet["option3"][index_L],
                                    text = "(3)",
                                    data = '3'
                                ),
                                PostbackTemplateAction(
                                    label = "(4) " + sheet["option4"][index_L],
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

#聽力測驗  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked_L
    global index_L
    global sheet
    global qNum

    if(isChangingLevel_L==True):
        levelinput = event.postback.data
        myResult = setLevel(levelinput) 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
    else:    
        print("correct answer = ",str(sheet["answer"][index_L]))
        print("index_L = ", index_L)
        answer = event.postback.data
        if answer != str(sheet["answer"][index_L]):
            feedback = sheet["feedback"][index_L]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
            isAsked_L = False       
        else:
            print('答對了！你真棒！')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '答對了！你真棒！'))
            isAsked_L = False

        if index_L < qNum - 1:
            index_L += 1
        else:
            index_L = 0
            sheet,qNum = getSheet(level_L)
            print("new sheet",sheet)
            print("new qNum",qNum)
        print("index_L after = ", index_L)

##聽力測驗  設定Level------------------------------------------------
def setLevel(levelinput):
    print("---Changing Level---")
    global sheet
    global qNum
    global level_L
    global isChangingLevel_L
   
    if (levelinput=='L'):
        level_L = 1
        isChangingLevel_L = False
        myResult= ("目前程度切換至初級 \n 請任意輸入 將開始出題～～")
        
    elif (levelinput=='M'):
        level_L = 2
        isChangingLevel_L = False
        myResult= ("目前程度切換至中級\n 請任意輸入 將開始出題～～")    
    elif (levelinput=='H'):
        level_L = 3
        isChangingLevel_L = False
        myResult= ("目前程度切換至高級\n 請任意輸入 將開始出題～～")  
    else:       
        isChangingLevel_L = True
        myResult = "N"
    
    if isChangingLevel_L == False:
        sheet,qNum = getSheet(level_L)
        print("level_L get sheet",sheet)
        print("level_L get qNum",qNum)
      
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

##  End------------------------------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
