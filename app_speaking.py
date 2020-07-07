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

##發音練習  import-----------------------------------------------
import sys
import datetime
import pygsheets

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,Type,point

##發音練習  變數------------------------------------------------

Type = 1 #預設Type 1
star_num = 0 #集點
isAsked = False
isChangingType = True
index = 0
# 初始抓資料＆資料處理------------------------------------------------
GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1gLGoiz9Sv-8hiqxm61dfdQi4WXXBvlst9Xod5b5Wl8M/edit#gid=1610920819'
sh = gc.open_by_url(survey_url)
sh.worksheet_by_title('Word').export(filename='Word')
sh.worksheet_by_title('Choose').export(filename='Choose')

Word = pd.read_csv('Word.csv') #Type: <class 'pandas.core.frame.DataFrame'>
Choose = pd.read_csv('Choose.csv')


def getSheet():  #打亂該sheet順序，並存成dictionary格式  
    
    sheet_Word = Word
    sheet_Choose = Choose

    return sheet_Word, sheet_Choose

def editSheet(data):
    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
    print("getSheet df = ",df)
    question = df.iloc[:,0]
    answer = df.iloc[:,1]
    sheet = {
        "question": question,
        "answer": answer
    }
    qNum = len(sheet["question"])
    return sheet,qNum

data_Word, data_Choose = getSheet()
sheet, qNum = editSheet(data_Word) 
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

##發音練習  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked
    global index
    global isChangingType
    global sheet
    replytext = event.message.text
    #myId = event.source.user_id
    if event.message.type == 'text':   
        if (isChangingType == True or replytext =='?'):   
            isChangingType = True      
            buttons_template = TemplateSendMessage (
                alt_text = 'Buttons Template',
                template = ButtonsTemplate (
                    title = '發音練習',
                    text = '念不出正確的發音嗎?',
                    thumbnail_image_url='https://upload.cc/i1/2020/05/18/V5TmMA.png',
                    actions = [
                            PostbackTemplateAction(
                                label = "單字發音", 
                                text = "單字發音",
                                data = 'V'
                            ),
                            PostbackTemplateAction(
                                label = "自行選擇發音題目",
                                text = "自行選擇發音題目",
                                data = 'T'
                            )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, buttons_template)
 
        else:
            if( isAsked == False ):                  
                question = sheet["question"][index]
                isAsked = True
                
                QA_BubbleContainer = BubbleContainer (
                    direction='ltr',
                    header = BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text="發音練習", weight='bold', size='lg', align = 'center')                   
                        ]
                    ),
                    body = BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text=question, weight='bold', size='xl', align = 'center') ,
                            TextComponent(text="請透過語音訊息唸給我聽", margin='none', size='sm', align = 'center',color='#727272') ,
                            SeparatorComponent(margin='xl',color='#A89F9F'),
                            ButtonComponent(
                                action = URIAction(label = '聽正確發音', uri = sheet["answer"][index]),
                                color = '#3B9A9C',
                                margin = 'lg',
                                style = 'primary',
                                flex = 10
                            ),
                            ButtonComponent(
                                action = PostbackAction(label = "下一題", data = 'next', text = "下一題"),
                                color = '#F8AF62',
                                margin = 'lg',
                                style = 'primary'
                            )
                        ]
                    )
                )                       
                message = FlexSendMessage(alt_text="QA_BubbleContainer", contents = QA_BubbleContainer)
                line_bot_api.reply_message(event.reply_token,message)

#發音練習  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked, index, sheet, qNum, star_num

    if(isChangingType==True):
        Typeinput = event.postback.data
        myResult = setType(Typeinput) 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
    
    else:    
        
        print('哇!完全正確！給你一個小星星!')
        star_num += 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '哇!完全正確！給你一個小星星!'))
        isAsked = False

        if index < qNum - 1:
            index += 1
        else:
            index = 0
        print("index after = ", index)

##發音練習  設定Type------------------------------------------------
def setType(Typeinput):
    print("---Changing Type---")
    global sheet, data_Word, data_Choose
    global qNum
    global Type
    global isChangingType,isAsked
   
    if (Typeinput=='V'):
        Type = 1
        isChangingType = False
        isAsked = False
        myResult= ("單字發音")
        data_Word, data_Choose = getSheet()
        sheet, qNum = editSheet(data_Word) 
        
        
    elif (Typeinput=='T'):
        Type = 2
        isChangingType = False
        isAsked = False
        myResult= ("自行選擇發音題目") 
        data_Word, data_Choose = getSheet()
        sheet, qNum = editSheet(data_Choose)   
    else:       
        isChangingType = True
        myResult = "N"
      
    return myResult
##發音練習  End------------------------------------------------
 
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
