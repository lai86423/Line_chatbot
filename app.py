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
import QA
##聽力測驗  import-----------------------------------------------
import sys
import datetime
import pygsheets
#TODO: 1.next bubble 的feedback 改成傳answer  2.變數全改 Ｌ 3.題目跟答案比對確認 

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level_L,point

##聽力  變數------------------------------------------------
level_L = 1 # 預設level 1
qNum = 10 # 每輪題目數量
star_num = 0 #集點
isAsked_L = False #出題與否
isChangingLevel_L = True
isStart = False
index_L = 0 #第幾題
isInit_L = True
subindex = 0
count = 1
##-----------------------------------------------------------------------------------
##聽力  初始抓資料＆資料處理
GDriveJSON = 'question.json'
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc = pygsheets.authorize(service_account_file='question.json') #檔案裡的google sheet js檔
survey_url_L = 'https://docs.google.com/spreadsheets/d/1e1hCM0yFzwQkzfdzJGCioLCvnPNJHw9IPHqz4sSEsjg/edit#gid=0'
sh_L = gc.open_by_url(survey_url_L)
sh_L.worksheet_by_title('L1_img').export(filename='L1_img')
sh_L.worksheet_by_title('L1_tail').export(filename='L1_tail')
sh_L.worksheet_by_title('L1_word').export(filename='L1_word')
sh_L.worksheet_by_title('L1_sen').export(filename='L1_sen')
sh_L.worksheet_by_title('L2_img').export(filename='L2_img')
sh_L.worksheet_by_title('L2_tail').export(filename='L2_tail')
sh_L.worksheet_by_title('L2_word').export(filename='L2_word')
sh_L.worksheet_by_title('L2_sen').export(filename='L2_sen')
sh_L.worksheet_by_title('L3_img').export(filename='L3_img')
sh_L.worksheet_by_title('L3_tail').export(filename='L3_tail')
sh_L.worksheet_by_title('L3_word').export(filename='L3_word')
sh_L.worksheet_by_title('L3_sen').export(filename='L3_sen')
#worksheet_list_L[11].export(filename='L3_sen')

L1_img = pd.read_csv('L1_img.csv') #type: <class 'pandas.core.frame.DataFrame'>
L1_tail = pd.read_csv('L1_tail.csv')
L1_word = pd.read_csv('L1_word.csv')
L1_sen = pd.read_csv('L1_sen.csv')
L2_img = pd.read_csv('L2_img.csv') 
L2_tail = pd.read_csv('L2_tail.csv') 
L2_word = pd.read_csv('L2_word.csv')
L2_sen = pd.read_csv('L2_sen.csv')
L3_img = pd.read_csv('L3_img.csv') 
L3_tail = pd.read_csv('L3_tail.csv') 
L3_word = pd.read_csv('L3_word.csv')
L3_sen = pd.read_csv('L3_sen.csv')
##----------------------------------------------------------------------------------
#三種問題類型
def getSheet(Qlevel):   
    if(Qlevel == 3):
        sheet_img = L3_img
        sheet_tail = L3_tail
        sheet_word = L3_word
        sheet_sen = L3_sen  

    elif(Qlevel == 2):
        sheet_img = L2_img
        sheet_tail = L2_tail
        sheet_word = L2_word
        sheet_sen = L2_sen 
    else:
        sheet_img = L1_img
        sheet_tail = L1_tail
        sheet_word = L1_word
        sheet_sen = L1_sen 

    return sheet_img, sheet_tail, sheet_word, sheet_sen

def editSheet(data):
    pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    question = pre_sheet.iloc[:,0]
    option1 = pre_sheet.iloc[:,1]
    option2 = pre_sheet.iloc[:,2]
    option3 = pre_sheet.iloc[:,3]
    option4 = pre_sheet.iloc[:,4]
    feedback = pre_sheet.iloc[:,5]
    answer = pre_sheet.iloc[:,6]
    sheet = {
        "question": question,
        "option1": option1,
        "option2": option2,
        "option3": option3,
        "option4": option4,
        "feedback": feedback,
        "answer": answer
    }
    #qNum = len(sheet["question"])
    return sheet

data_img, data_tail, data_word, data_sen = getSheet(level_L)
sheet = editSheet(data_img) 
##-----------------------------------------------------------------------------------
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
#處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    global isAsked_L,isInit_L
    global index_L
    global isChangingLevel_L
    global sheet,subindex
    replytext = event.message.text
    myId = event.source.user_id
    if event.message.type == 'text':   
        if(isInit_L == True or replytext =='?'):
            isChangingLevel_L = True
            message = TextSendMessage(text="歡迎來到聽力練習！\n\n在這邊可以選擇適合你的難易度。\n\n題目分為發音、詞彙以及句子，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
            line_bot_api.push_message(myId, message)
            isInit_L=False
        if(isChangingLevel_L == True):   
            isAsked_L = False
            setlevel_bubble = levelBubble()
            line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
        elif isStart == True:
            if( isAsked_L == False ): 
                isAsked_L = True
                QA_bubble = Question()
                message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                line_bot_api.reply_message(event.reply_token, message)
##-----------------------------------------------------------------------------------
#回饋判斷
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    global isAsked_L,isStart,isChangingLevel_L
    global index_L,sheet,subindex
    global qNum, star_num
    global data_img, data_tail, data_word, data_sen, count

    if(isChangingLevel_L==True):
        level_bubble = setLevel(event.postback.data) 
        message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
        line_bot_api.reply_message(event.reply_token,message) 

    elif(event.postback.data == "start"):  
        isStart = True
    elif(isStart == True): 
        print("correct answer = ",str(sheet["answer"][subindex]))
        print("answer index_L = ", index_L)
        print("answer subindex = ", subindex)
        answer = event.postback.data
        if(index_L < qNum): #做完本輪題庫數目
            print('count: ', count)
            print('index_L: ', index_L)
            if answer != str(sheet["answer"][subindex]):
                feedback = sheet["feedback"][subindex]
                #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
                if(count != 0):
                    isStart = False
                    wrongBubble = tryagainBubble()
                    message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    count -= 1
                elif(count == 0):
                    isStart = False
                    loseBubble = nextBubble(feedback)
                    message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    count = 1
                    index_L += 1
                isAsked_L = False
            else:
                isStart = False
                star_num += count
                #score += count
                #lis_score += count
                #print('score: ', score)
                #print('lis_score: ', lis_score)
                #user_sheet.update_cell(score_row, 2, score)
                #user_sheet.update_cell(score_row, 4, lis_score)
                #print('save!!!!!!!!!!')
                print('正確答案!')
                if(count == 1):
                    reply = '你好棒!一次就答對了!'
                elif(count == 0):
                    reply = '好棒哦!你答對了!'
                print(count, reply)
                if(index_L == 9):
                    reply = '好棒哦!你答對了!'
                    correctBubble = finalBubble(reply)
                else:
                    correctBubble = rightBubble(reply)
                message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                line_bot_api.reply_message(event.reply_token,message)
                #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '恭喜你答對了!給你一個小星星!\n'))
                index_L += 1
                if(index_L < 10):
                    isAsked_L = False
                count = 1
            print('after count: ', count)
            print('after index_L: ', index_L)
    
    elif(event.postback.data == "end"):
        #print('恭喜你做完這次的聽力練習了!star=',star_num)
        starBubble = totalStarBubble()
        message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
        line_bot_api.reply_message(event.reply_token,message)
        isStart = False

    elif (event.postback.data == "next"): 
        index_L = 0
        star_num = 0
        print("答題分數顯示完 圖數和分數歸零----",index_L,star_num)
        changelevel_bubble = changeLevelBubble()
        message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
        line_bot_api.reply_message(event.reply_token, message)  

    elif (event.postback.data == "changeLevel"): 
        isChangingLevel_L = True

    elif (event.postback.data == "next2"):
        isStart = True
        print("restart isAsked_L",isAsked_L)
        print("restart QA_bubble")
        isAsked_L = True
        QA_bubble = Question()
        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
        line_bot_api.reply_message(event.reply_token, message)
        
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
    global subindex,sheet
    print("選完階級！開始出題")
    print("index_L",index_L)
    if index_L < 3:
        if level_L != 3:
            sheet = editSheet(data_tail)
            QA_bubble = QA.QA_Tail(sheet,index_L,index_L)
        else: #高級前三題，題目不同
            sheet = editSheet(data_sen) 
            QA_bubble = QA.QA_Sentence(sheet,index_L,subindex,'依據音檔，選出最適當的答案')
    elif index_L < 7:
        subindex = index_L-3
        sheet = editSheet(data_word)
        QA_bubble = QA.QA_Word(sheet,index_L,subindex)
    else:
        subindex = index_L-7
        sheet = editSheet(data_sen) 
        QA_bubble = QA.QA_Sentence(sheet,index_L,subindex,'選出正確的應對句子')
    return QA_bubble
##-----------------------------------------------------------------------------------
#Bubble Template------------------------------------------------
def levelBubble():
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '聽力練習',
                        text = '總是聽不懂別人在說什麼嗎?',
                        thumbnail_image_url='https://upload.cc/i1/2020/06/08/jhziMK.png',
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

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)