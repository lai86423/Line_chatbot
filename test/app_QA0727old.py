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
import UIBubble_QA

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level,point

##出題小老師  變數------------------------------------------------

level = 1 #預設level 1
qNum = 10 # 每輪題目數量
star_num = 0 #集點
isAsked = False
isChangingLevel = True
isInit = True
isStart = False
index = 0
subindex = 0
count = 1

isChangingType = False
# 初始抓資料＆資料處理------------------------------------------------
GDriveJSON = 'question.json'
GSpreadSheet = 'cilab_ChatBot_QA'
gc = pygsheets.authorize(service_account_file='question.json')
survey_url = 'https://docs.google.com/spreadsheets/d/1Zf5Qr_dp5GjYZJbxuVKl283fIRKUgs2q9nYNBeTWKJ8/edit#gid=0'
sh = gc.open_by_url(survey_url)
sh.worksheet_by_title('L1_Voc').export(filename='L1_Voc')
sh.worksheet_by_title('L1_Reading').export(filename='L1_Reading')
sh.worksheet_by_title('L1_Cloze').export(filename='L1_Cloze')
sh.worksheet_by_title('L2_Voc').export(filename='L2_Voc')
sh.worksheet_by_title('L2_Reading').export(filename='L2_Reading')
sh.worksheet_by_title('L2_Cloze').export(filename='L2_Cloze')
sh.worksheet_by_title('L3_Voc').export(filename='L3_Voc')
sh.worksheet_by_title('L3_Reading').export(filename='L3_Reading')
sh.worksheet_by_title('L3_Cloze').export(filename='L3_Cloze')

L1_Voc = pd.read_csv('L1_Voc.csv') #type: <class 'pandas.core.frame.DataFrame'>
L1_Reading = pd.read_csv('L1_Reading.csv')
L1_Cloze = pd.read_csv('L1_Cloze.csv')
L2_Voc = pd.read_csv('L2_Voc.csv') 
L2_Reading = pd.read_csv('L2_Reading.csv') 
L2_Cloze = pd.read_csv('L2_Cloze.csv')
L3_Voc = pd.read_csv('L3_Voc.csv') 
L3_Reading = pd.read_csv('L3_Reading.csv') 
L3_Cloze = pd.read_csv('L3_Cloze.csv')

##----------------------------------------------------------------------------------
#三種問題類型
def getSheet(level):  #打亂該sheet順序，並存成dictionary格式  
    if(level == 3):
        sheet_Voc = L3_Voc
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze
    elif(level == 2):
        sheet_Voc = L3_Voc
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze
    else:
        sheet_Voc = L3_Voc
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze
    return sheet_Voc, sheet_Reading, sheet_Cloze

def editSheet(data):
    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
    print("getSheet df = ",df)
    question = df.iloc[:,0]
    option1 = df.iloc[:,1]
    option2 = df.iloc[:,2]
    option3 = df.iloc[:,3]
    answer = df.iloc[:,4]
    sheet = {
        "question": question,
        "option1": option1,
        "option2": option2,
        "option3": option3,
        "answer": answer
    }
    qNum = len(sheet["question"])
    return sheet,qNum

data_Voc, data_Reading, data_Cloze = getSheet(level)
sheet, qNum = editSheet(data_Voc) 
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
##-----------------------------------------------------------------------------------
##出題小老師  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked,isInit
    global index
    global isChangingLevel
    global sheet,subindex
    replytext = event.message.text
    myId = event.source.user_id
    if event.message.type == 'text':   
       if(isInit == True or replytext =='?'):
            isChangingLevel = True
            message = TextSendMessage(text="歡迎來到解題小達人！\n\n在這邊可以選擇適合你的難易度來挑戰，一組題目有10題。\n\n題目分為詞彙題、克漏字以及閱讀測驗，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
            line_bot_api.push_message(myId, message)
            isInit = False
        if(isChangingLevel == True ):
            isAsked = False
            setlevel_bubble = levelBubble()
            line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
        elif isStart == True:
            if( isAsked == False ): 
                isAsked = True
                print("Asking!")
                #QA_bubble = Question()
                #message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                #line_bot_api.reply_message(event.reply_token, message)                

    #print("=======Reply Token=======")
    #print(event.reply_token)
    #print("=========================")

#出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked, index, sheet, qNum, star_num

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
            print('恭喜你答對了!給你一個小星星!')
            star_num += 1
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '恭喜你答對了!給你一個小星星!'))
            isAsked = False

        if index < qNum - 1:
            index += 1
        else:
            index = 0
        print("index after = ", index)
##-----------------------------------------------------------------------------------
#設定Level------------------------------------------------
def setLevel(levelinput):
    print("---Changing Level---")
    global data_img, data_tail, data_word, data_sen
    global level_L
    global isChangingLevel_L
    
    if (levelinput=='L'):
        level_L = 1
        myResult = readyBubble(level_L)
        isChangingLevel_L = False
        
    elif (levelinput=='M'):
        level_L = 2
        myResult = readyBubble(level_L)    
        isChangingLevel_L = False

    elif (levelinput=='H'):
        level_L = 3
        myResult = readyBubble(level_L)
        isChangingLevel_L = False

    else:       
        isChangingLevel_L = True
        myResult = "N"

    if isChangingLevel_L == False:
        data_img, data_tail, data_word, data_sen = getSheet(level_L)
        #sheet = editSheet(pre_sheet)
        print("更換難易度後 更新取得新的隨機題目----level_L get sheet",sheet)
      
    return myResult

def Question():
    print("選完階級！開始出題")
    print("index_L",index_L)
    if index_L < 3:
        print("type 1 Q")
        sheet = editSheet(data_tail)
        QA_bubble = UIBubble_QA.QA_Tail(sheet,index_L,index_L)
    elif index_L < 7:
        subindex = index_L-3
        sheet = editSheet(data_word)
        print("type 2 Q")
        QA_bubble = UIBubble_QA.QA_Word(sheet,index_L,subindex)
    else:
        subindex = index_L-7
        sheet = editSheet(data_sen) 
        print("type 3 Q")
        QA_bubble = UIBubble_QA.QA_Sentence(sheet,index_L,subindex)
    return QA_bubble
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

##-----------------------------------------------------------------------------------
#Bubble Template------------------------------------------------
def levelBubble():
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '解題小達人',
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
    return level_template

def readyBubble(level):
    if level == 1:
        leveltext = '初級難易度！'
    elif level == 2:
        leveltext ='中級難易度！'
    else:
        leveltext ='高級難易度！'
    print("leveltext",leveltext)   
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="準備好了嗎?", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="你選擇的是" + leveltext, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '開始答題', data = 'start', text = '開始答題'),
                    color = '#F8AF62',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble 

def totalStarBubble():
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="獲得星星!!", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        hero= ImageComponent(
            url="https://upload.cc/i1/2020/07/01/pDbGXh.png", size='full', aspect_ratio="1.51:1",aspect_mode="cover"
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="恭喜你獲得了" + str(star_num) + "顆星星!" , size='xs', align = 'center'),
                SeparatorComponent(margin='md'),
                ButtonComponent(
                    action = PostbackAction(label = "下一大題", data = 'next', text = "下一大題"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "我不答了", data = 'end', text = "我不答了"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble 

def changeLevelBubble():
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = "更換難易度", data = 'changeLevel', text = "更換難易度"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "不用，繼續下一大題", data = 'next2', text = "不用，繼續下一大題"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble 

def rightBubble(reply): 
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="恭喜答對!!", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= reply, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '下一題', data = 'start', text = '下一題'),
                    color = '#F8AF62',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble

def tryagainBubble():
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="請再想想!!", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="答案不對哦~你再想想看!", size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '再試一次', data = 'start', text = '再試一次'),
                    color = '#F8AF62',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble

def nextBubble(feedback):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= '再接再厲', weight='bold', size='xl', align = 'center')               
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= feedback, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '跳下一題', data = 'start', text = '下一題'),
                    color = '#45E16E',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble

def finalBubble(reply):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= '恭喜答對!!', weight='bold', size='xl', align = 'center')               
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= '好棒哦!你答對了!', size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '結束作答', data = 'end', text = '結束作答'),
                    color = '#E15B45',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble
##  End------------------------------------------------
##出題小老師  End------------------------------------------------

##出題小老師  設定Level------------------------------------------------
def setLevel_old(levelinput):
    print("---Changing Level---")
    global sheet, data_Voc, data_Reading, data_Cloze
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
        data_Voc, data_Reading, data_Cloze = getSheet(level)
      
    return myResult
##出題小老師  設定出題類型------------------------------------------------
def setType_old(typeinput) :
    print("---Changing Level---")
    global sheet, qNum
    global isChangingType
    
    if (typeinput=='W'):
        sheet, qNum = editSheet(data_Voc) 
        isChangingType = False
        myResult= ("題目類型切換至詞彙練習")
        
    elif (typeinput=='G'):
        sheet, qNum = editSheet(data_Reading) 
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

# ##-----------選完階級選出題類型
# elif(isChangingType == True):
#     QAsort_bubble = typeButton()
#     message = FlexSendMessage(alt_text="QAsort_bubble", contents = QAsort_bubble)
#     line_bot_api.reply_message(event.reply_token,message) 
    
# else:
#     if( isAsked == False ):  
# question = sheet["question"][index]
# print(question)
# print("1:", sheet["option1"][index], "\n2:", sheet["option2"][index], "\n3:", sheet["option3"][index],
#         "\n4:", "\n")
# isAsked = True

# QA_BubbleContainer = BubbleContainer (
#     direction='ltr',
#     header = BoxComponent(
#         layout='vertical',
#         contents=[
#             TextComponent(text=question, size='lg', align = 'start',gravity='top')                   
#         ]
#     ),
#     body = BoxComponent(
#         layout='vertical',
#         contents=[
#             ButtonComponent(
#                 action = PostbackAction(label = "1. " +sheet["option1"][index], data = '1', text = "1. " +sheet["option1"][index]),
#                 color = '#46549B',
#                 margin = 'md',
#                 style = 'primary'
#             ),
#                 ButtonComponent(
#                 action = PostbackAction(label = "2. " +sheet["option2"][index], data = '2', text = "2. " +sheet["option2"][index]),
#                 color = '#7E318E',
#                 margin = 'md',
#                 style = 'primary'
#             ),
#                 ButtonComponent(
#                 action = PostbackAction(label = "3. " +sheet["option3"][index], data = '3', text = "3. " +sheet["option3"][index]),
#                 color = '#CD2774',
#                 margin = 'md',
#                 style = 'primary',
#                 gravity='top'
#             )
#         ]
#     )
# )                       
# message = FlexSendMessage(alt_text="QA_BubbleContainer", contents = QA_BubbleContainer)
# line_bot_api.reply_message(event.reply_token,message)
