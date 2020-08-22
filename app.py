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
import random
from googletrans import Translator
import QA
##import-----------------------------------------------
import sys
import datetime
import pygsheets
import QA_Bubble
import getVoc

import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level_Q,point

allUser = [] 
##-----------------------------------------------------------------------------------
##出題  初始抓資料＆資料處理
GDriveJSON = 'question.json'
GSpreadSheet_Q = 'cilab_ChatBot_QA'
gc_Q = pygsheets.authorize(service_account_file='question.json')
survey_url_Q = 'https://docs.google.com/spreadsheets/d/1R2l0OQENJjnMhWK1M6fXxet-e12V-AsR/edit#gid=1449448532'
sh_Q = gc_Q.open_by_url(survey_url_Q)
sh_Q.worksheet_by_title('L1_Reading').export(filename='L1_Reading')
sh_Q.worksheet_by_title('L1_Cloze').export(filename='L1_Cloze')
sh_Q.worksheet_by_title('L2_Reading').export(filename='L2_Reading')
sh_Q.worksheet_by_title('L2_Cloze').export(filename='L2_Cloze')
sh_Q.worksheet_by_title('L3_Reading').export(filename='L3_Reading')
sh_Q.worksheet_by_title('L3_Cloze').export(filename='L3_Cloze')

#type: <class 'pandas.core.frame.DataFrame'
L1_Reading = pd.read_csv('L1_Reading.csv')
L1_Cloze = pd.read_csv('L1_Cloze.csv')
L2_Reading = pd.read_csv('L2_Reading.csv') 
L2_Cloze = pd.read_csv('L2_Cloze.csv')
L3_Reading = pd.read_csv('L3_Reading.csv') 
L3_Cloze = pd.read_csv('L3_Cloze.csv')

##----------------------------------------------------------------------------------
#三種問題類型
def getSheet(Qlevel):   
    if(Qlevel == 3):
        #sheet_Voc = L3_Voc
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze 

    elif(Qlevel == 2):
        #sheet_Voc = L2_Voc
        sheet_Reading = L2_Reading
        sheet_Cloze = L2_Cloze
    else:
        #sheet_Voc = L1_Voc
        sheet_Reading = L1_Reading
        sheet_Cloze = L1_Cloze
    
    sheet_Voc = getVoc.getSheet(Qlevel)
    #sheet_Voc = getVoc.editSheet(presheet_Voc)
    
    return sheet_Voc, sheet_Reading, sheet_Cloze

def editSheet(data):
    pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    print("header",pre_sheet.columns)
    header = pre_sheet.columns
    sheet_Q = {}
    for i in range (len(header)):
        sheet_Q[header[i]] = pre_sheet[header[i]]

    return sheet_Q

##TODO 個人ＩＤ變數------------------------------------------------
class userVar_Q():
    def __init__(self,_id):
        self._id = _id
        self.level_Q = 1 # 預設level 1
        self.qNum_Q = 10 # 每輪題目數量
        self.star_num_Q = 0 #集點
        self.isAsked_Q = False #出題與否
        self.isChangingLevel_Q = True
        self.isStart_Q = False
        self.index_Q = 0 #第幾題
        self.isInit_Q = True
        self.subindex_Q = self.index_Q
        self.count_Q = 1
        self.data_Voc, self.data_Reading, self.data_Cloze = getSheet(self.level_Q) #預設傳level = 1
        self.sheet_Q = getVoc.editSheet(self.data_Voc)
        self.isVoc = False 
        self.VocQA = []

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
    user = getUser(event.source.user_id)
    #---------------------------------------
    if event.message.type == 'text':   
        if(user.isInit_Q == True or event.message.text =='?'):
            user.isChangingLevel_Q = True
            message = TextSendMessage(text="歡迎來到解題小達人！\n\n在這邊可以選擇適合你的難易度來挑戰，一組題目有10題。\n\n題目分為詞彙題、克漏字以及閱讀測驗，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
            line_bot_api.push_message(user._id, message)
            user.isInit_Q=False
        if(user.isChangingLevel_Q == True):   
            user.isAsked_Q = False
            setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/V5TmMA.png','解題小達人', '總是聽不懂別人在說什麼嗎?')
            line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
        elif user.isStart_Q == True:
            if( user.isAsked_Q == False ): 
                user.isAsked_Q = True
                QA_bubble = Question(user)
                message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                line_bot_api.reply_message(event.reply_token, message)
##-----------------------------------------------------------------------------------
def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar_Q(user_ID)
        allUser.append(user)
        print("Alluser",allUser)
    return user 

#回饋判斷
@handler.add(PostbackEvent)
def handle_postback(event):
    user = getUser(event.source.user_id)
    print("postbackData = ",event.postback.data )
    if(user.isChangingLevel_Q==True):
        level_bubble = setLevel(event.postback.data,user) 
        message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
        line_bot_api.reply_message(event.reply_token,message) 

    elif(event.postback.data == "start"):  #第七題開始需要先主動送文章再出題
        if(user.index_Q == 7 and user.count_Q == 1):
            sheet_article = editSheet(user.data_Reading) 
            QA_bubble_article = QA_Bubble.Article(sheet_article,user.subindex_Q)
            article = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble_article)
            line_bot_api.push_message(event.source.user_id, article)
        user.isStart_Q = True

    elif(user.isStart_Q == True):
        if user.isVoc == True:
            correctAns = str(user.VocQA[user.index_Q][2])
        else:
            correctAns = str(user.sheet_Q["answer"][user.subindex_Q])

        print("correct answer = ",correctAns)
        print("answer index_Q = ", user.index_Q)
        print("answer subindex_Q = ", user.subindex_Q)

        if(user.index_Q < user.qNum_Q): #做完本輪題庫數目
            #print('count_Q: ', user.count_Q)
            if event.postback.data != correctAns:
                if(user.count_Q != 0):
                    user.isStart_Q = False
                    wrongBubble = tryagainBubble("請再想想!!", "答案不對哦~你再想想看!", 'start')
                    message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.count_Q -= 1
                elif(user.count_Q == 0):
                    user.isStart_Q = False
                    if(user.index_Q == 9):
                        loseBubble = finalBubble('再接再厲！!', '好可惜哦~答案是('+ correctAns +')才對哦!')
                    else:    
                        loseBubble = nextBubble('好可惜哦~答案是('+ correctAns +')才對哦!','再接再厲')
                    message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.count_Q = 1
                    user.index_Q += 1
                user.isAsked_Q = False
            else:
                user.isStart_Q = False
                user.star_num_Q += user.count_Q
                print('正確答案!')
                if(user.count_Q == 1):
                    reply = '你好棒!一次就答對了!'
                elif(user.count_Q == 0):
                    reply = '好棒哦!你答對了!'
                #print(user.count_Q, reply)
                if(user.index_Q == 9):
                    print("last Q")
                    reply = '好棒哦!你答對了!'
                    correctBubble = finalBubble('恭喜答對!!', '好棒哦!你答對了!')

                else:
                    correctBubble = rightBubble(reply)
                message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                line_bot_api.reply_message(event.reply_token,message)
                user.index_Q += 1
                if(user.index_Q < 10):
                    user.isAsked_Q = False
                user.count_Q = 1
            print('after count_Q: ', user.count_Q)
            print('after index_Q: ', user.index_Q)
    
    elif(event.postback.data == "end"):
        #print('恭喜你做完這次的聽力練習了!star=',star_num_Q)
        starBubble = totalStarBubble(user)
        message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
        line_bot_api.reply_message(event.reply_token,message)
        user.isStart_Q = False

    elif (event.postback.data == "next"): 
        user.index_Q = 0
        user.star_num_Q = 0
        #TODO
        user.VocQA = []
        print("答題分數顯示完 圖數和分數歸零----",user.index_Q,user.star_num_Q)
        changelevel_bubble = changeLevelBubble()
        message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
        line_bot_api.reply_message(event.reply_token, message)  

    elif (event.postback.data == "changeLevel"): 
        user.isChangingLevel_Q = True

    elif (event.postback.data == "next2"):
        user.isStart_Q = True
        user.isAsked_Q = True
        QA_bubble = Question(user)
        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
        line_bot_api.reply_message(event.reply_token, message)
    elif (event.postback.data == "AllEnd"):
        message = TextSendMessage(text="謝謝你使用解題小達人～～\n歡迎點開下方選單，使用其他功能使用其他功能哦！")
        line_bot_api.reply_message(event.reply_token, message)
        
##-----------------------------------------------------------------------------------
#設定Level------------------------------------------------
def setLevel(levelinput,user):
    print("---Changing Level---")
    if (levelinput=='L'):
        user.level_Q = 1
        myResult = readyBubble(user.level_Q)
        user.isChangingLevel_Q = False
        
    elif (levelinput=='M'):
        user.level_Q = 2
        myResult = readyBubble(user.level_Q)    
        user.isChangingLevel_Q = False

    elif (levelinput=='H'):
        user.level_Q = 3
        myResult = readyBubble(user.level_Q)
        user.isChangingLevel_Q = False

    else:       
        user.isChangingLevel_Q = True
        myResult = "N"

    if user.isChangingLevel_Q == False:
        user.data_Voc, user.data_Reading, user.data_Cloze = getSheet(user.level_Q)
      
    return myResult

def Question(user):
    print("選完階級開始出題")
    if user.index_Q < 3:
        user.isVoc = True
        try:
            print(user.VocQA[user.index_Q])
            QA_bubble = QA_Bubble.Voc(user.index_Q, user.VocQA[user.index_Q])
        except: 
            user.sheet_Q = getVoc.editSheet(user.data_Voc)
            q_index, q_chinese, q_english = getVoc.getVoc(user.sheet_Q)
            option_english,option_english2 = getVoc.getOption(user.data_Voc, q_index)
            option, answer = getVoc.getQA(q_english, option_english,option_english2)
            templist = [q_chinese, option, answer]
            print(templist)
            user.VocQA.append(templist)
            print(user.VocQA[user.index_Q])
            QA_bubble = QA_Bubble.Voc(user.index_Q, user.VocQA[user.index_Q])
    
    elif user.index_Q < 7:
        user.isVoc = False
        user.subindex_Q = user.index_Q - 3
        user.sheet_Q = editSheet(user.data_Cloze)
        QA_bubble = QA_Bubble.Cloze(user.sheet_Q,user.index_Q,user.subindex_Q)

    else:
        user.subindex_Q = user.index_Q - 7
        user.sheet_Q = editSheet(user.data_Reading) 
        QA_bubble = QA_Bubble.Reading(user.sheet_Q,user.index_Q,user.subindex_Q)
        
    return QA_bubble

##-----------------------------------------------------------------------------------
#Bubble Template------------------------------------------------
def levelBubble(pic_url,str1, str2):
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = str1,
                        text = str2,
                        thumbnail_image_url=pic_url,
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

def totalStarBubble(user):
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
                TextComponent(text="恭喜你獲得了" + str(user.star_num_Q) + "顆星星!" , size='xs', align = 'center'),
                SeparatorComponent(margin='md'),
                ButtonComponent(
                    action = PostbackAction(label = "下一大題", data = 'next', text = "下一大題"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "我不答了", data = 'AllEnd', text = "我不答了"),
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

def tryagainBubble(str1, str2, str3):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text=str1, weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text=str2, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '再試一次', data = str3, text = '再試一次'),
                    color = '#F8AF62',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble
def nextBubble(feedback, str):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= str, weight='bold', size='xl', align = 'center')               
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

def finalBubble(str1, str2):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= str1, weight='bold', size='xl', align = 'center')               
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= str2, size='xs', align = 'center', gravity = 'top'),
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