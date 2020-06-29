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

##出題小老師  變數------------------------------------------------

level = 1 #預設level 1
isAsked = False
isChangingLevel = True
isChangingType = False
index = 0
# 初始抓資料＆資料處理------------------------------------------------
GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_test'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1Zf5Qr_dp5GjYZJbxuVKl283fIRKUgs2q9nYNBeTWKJ8/edit#gid=0'
sh = gc.open_by_url(survey_url)
sh.worksheet_by_title('L1_Word').export(filename='L1_Word')
sh.worksheet_by_title('L1_Grammar').export(filename='L1_Grammar')
sh.worksheet_by_title('L1_Cloze').export(filename='L1_Cloze')
sh.worksheet_by_title('L2_Word').export(filename='L2_Word')
sh.worksheet_by_title('L2_Grammar').export(filename='L2_Grammar')
sh.worksheet_by_title('L2_Cloze').export(filename='L2_Cloze')
sh.worksheet_by_title('L3_Word').export(filename='L3_Word')
sh.worksheet_by_title('L3_Grammar').export(filename='L3_Grammar')
sh.worksheet_by_title('L3_Cloze').export(filename='L3_Cloze')

L1_Word = pd.read_csv('L1_Word.csv') #type: <class 'pandas.core.frame.DataFrame'>
L1_Grammar = pd.read_csv('L1_Grammar.csv')
L1_Cloze = pd.read_csv('L1_Cloze.csv')
L2_Word = pd.read_csv('L2_Word.csv') 
L2_Grammar = pd.read_csv('L2_Grammar.csv') 
L2_Cloze = pd.read_csv('L2_Cloze.csv')
L3_Word = pd.read_csv('L3_Word.csv') 
L3_Grammar = pd.read_csv('L3_Grammar.csv') 
L3_Cloze = pd.read_csv('L3_Cloze.csv')



def getSheet(level):  #打亂該sheet順序，並存成dictionary格式  
    if(level == 3):
        sheet_Word = L3_Word
        sheet_Grammar = L3_Grammar
        sheet_Cloze = L3_Cloze
    elif(level == 2):
        sheet_Word = L3_Word
        sheet_Grammar = L3_Grammar
        sheet_Cloze = L3_Cloze
    else:
        sheet_Word = L3_Word
        sheet_Grammar = L3_Grammar
        sheet_Cloze = L3_Cloze
    return sheet_Word, sheet_Grammar, sheet_Cloze

def editSheet(data):
    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
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

data_Word, data_Grammar, data_Cloze = getSheet(level)
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

##出題小老師  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked
    global index
    global isChangingLevel
    global sheet
    replytext = event.message.text
    #myId = event.source.user_id
    if event.message.type == 'text':   
        if (isChangingLevel == True or replytext =='?'):   
            isChangingLevel = True
            isAsked = False
            buttons_template = TemplateSendMessage (
                alt_text = 'Buttons Template',
                template = ButtonsTemplate (
                    title = '出題小老師',
                    text = '想要自我檢測學習英文嗎?',
                    thumbnail_image_url='https://upload.cc/i1/2020/05/18/V5TmMA.png',
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

        ##-----------選完階級選出題類型
        elif(isChangingType == True):
            QAsort_bubble = typeButton()
            message = FlexSendMessage(alt_text="QAsort_bubble", contents = QAsort_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
            
        else:
            if( isAsked == False ):                  
                question = sheet["question"][index]
                print(question)
                print("1:", sheet["option1"][index], "\n2:", sheet["option2"][index], "\n3:", sheet["option3"][index],
                        "\n4:", sheet["option4"][index], "\n")
                isAsked = True
                
                QA_BubbleContainer = BubbleContainer (
                    direction='ltr',
                    header = BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text=question, weight='bold', size='lg', align = 'start',gravity='top')                   
                        ]
                    ),
                    body = BoxComponent(
                        layout='vertical',
                        contents=[
                            ButtonComponent(
                                action = PostbackAction(label = "1. " +sheet["option1"][index], data = '1', text = "1. " +sheet["option1"][index]),
                                color = '#46549B',
                                margin = 'md',
                                style = 'primary'
                            ),
                                ButtonComponent(
                                action = PostbackAction(label = "2. " +sheet["option2"][index], data = '2', text = "2. " +sheet["option2"][index]),
                                color = '#7E318E',
                                margin = 'md',
                                style = 'primary'
                            ),
                                ButtonComponent(
                                action = PostbackAction(label = "3. " +sheet["option3"][index], data = '3', text = "3. " +sheet["option3"][index]),
                                color = '#CD2774',
                                margin = 'md',
                                style = 'primary',
                                gravity='top'
                            )
                        ]
                    )
                )                       
                message = FlexSendMessage(alt_text="QA_BubbleContainer", contents = QA_BubbleContainer)
                line_bot_api.reply_message(event.reply_token,message)
    #print("=======Reply Token=======")
    #print(event.reply_token)
    #print("=========================")

#出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked, index, sheet, qNum

    if(isChangingLevel==True):
        levelinput = event.postback.data
        myResult = setLevel(levelinput) 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
    
    elif(isChangingType == True):
        typeinput = event.postback.data
        typeResult = setType(typeinput) 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = typeResult))
    
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
        print("index after = ", index)

##出題小老師  設定Level------------------------------------------------
def setLevel(levelinput):
    print("---Changing Level---")
    global sheet, data_Word, data_Grammar, data_Cloze
    global qNum
    global level
    global isChangingLevel,isChangingType
   
    if (levelinput=='L'):
        level = 1
        isChangingLevel = False
        isChangingType = True
        myResult= ("目前程度切換至初級")
        
    elif (levelinput=='M'):
        level = 2
        isChangingLevel = False
        isChangingType = True
        myResult= ("目前程度切換至中級")    
    elif (levelinput=='H'):
        level = 3
        isChangingLevel = False
        isChangingType = True
        myResult= ("目前程度切換至高級")  
    else:       
        isChangingLevel = True
        myResult = "N"
    
    if isChangingLevel == False:
        data_Word, data_Grammar, data_Cloze = getSheet(level)
      
    return myResult
##出題小老師  設定出題類型------------------------------------------------
def setType(typeinput) :
    print("---Changing Level---")
    global sheet, qNum
    global isChangingType
    
    if (typeinput=='W'):
        sheet, qNum = editSheet(data_Word) 
        isChangingType = False
        myResult= ("題目類型切換至詞彙練習")
        
    elif (typeinput=='G'):
        sheet, qNum = editSheet(data_Grammar) 
        isChangingType = False
        myResult= ("題目類型切換至文法練習")    
    elif (typeinput=='C'):
        sheet, qNum = editSheet(data_Cloze) 
        isChangingType = False
        myResult= ("題目類型切換至克漏字練習")  
    else:       
        isChangingType = True
        myResult = "N"
    
    return myResult
##出題小老師  出題類型ＵＩ------------------------------------------------
def typeButton():
    QAsort_bubble = BubbleContainer (
                header = BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text='請選擇題目類型', weight='bold', size='xl', color = '#000000')                   
                    ]
                ),
                body = BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action = PostbackAction(label = '詞彙練習', data = 'W', text = '詞彙練習'),
                            color = '#001774',
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '文法練習', data = 'G', text = '文法練習'),
                            color = '#FF595D',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '克漏字練習', data = 'C', text = '克漏字練習'),
                            color = '#FFB54A',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        )
                    ]
                )
            )   
            
    return QAsort_bubble
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
