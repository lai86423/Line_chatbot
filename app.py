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
import getVoc

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,user.level_L,point


allUser = [] 

##-----------------------------------------------------------------------------------
##聽力  初始抓資料＆資料處理
GDriveJSON = 'JSON.json'
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc_L = pygsheets.authorize(service_account_file='JSON.json') #檔案裡的google user.sheet_L js檔
sh_L = gc_L.open(GSpreadSheet_L)
sh_L.worksheet_by_title('L1_pho').export(filename='L1_pho')
#sh_L.worksheet_by_title('L1_word').export(filename='L1_word')
sh_L.worksheet_by_title('L1_sen').export(filename='L1_sen')
sh_L.worksheet_by_title('L2_pho').export(filename='L2_pho')
#sh_L.worksheet_by_title('L2_word').export(filename='L2_word')
sh_L.worksheet_by_title('L2_sen').export(filename='L2_sen')
sh_L.worksheet_by_title('L3_pho').export(filename='L3_pho')
#sh_L.worksheet_by_title('L3_word').export(filename='L3_word')
sh_L.worksheet_by_title('L3_sen').export(filename='L3_sen')

#type: <class 'pandas.core.frame.DataFrame'>
L1_pho = pd.read_csv('L1_pho.csv')
#L1_word = pd.read_csv('L1_word.csv')
L1_sen = pd.read_csv('L1_sen.csv')
L2_pho = pd.read_csv('L2_pho.csv') 
#L2_word = pd.read_csv('L2_word.csv')
L2_sen = pd.read_csv('L2_sen.csv')
L3_pho = pd.read_csv('L3_pho.csv') 
#L3_word = pd.read_csv('L3_word.csv')
L3_sen = pd.read_csv('L3_sen.csv')
##----------------------------------------------------------------------------------
#三種問題類型
def getSheet(Qlevel):   
    if(Qlevel == 3):
        sheet_pho = L3_pho
        #sheet_word = L3_word
        sheet_sen = L3_sen  

    elif(Qlevel == 2):
        sheet_pho = L2_pho
        #sheet_word = L2_word
        sheet_sen = L2_sen 
    else:
        sheet_pho = L1_pho
        #sheet_word = L1_word
        sheet_sen = L1_sen 
    
    sheet_word = getVoc.getSheet(Qlevel)
    
    return sheet_pho, sheet_word, sheet_sen

def editSheet(data):
    # presheet  = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    # question = presheet .iloc[:,0]
    # option1 = presheet .iloc[:,1]
    # option2 = presheet .iloc[:,2]
    # option3 = presheet .iloc[:,3]
    # #option4 = presheet .iloc[:,4]
    # feedback = presheet .iloc[:,5]
    # answer = presheet .iloc[:,6]
    # sheet = {
    #     "question": question,
    #     "option1": option1,
    #     "option2": option2,
    #     "option3": option3,
    #     "option4": option4,
    #     "feedback": feedback,
    #     "answer": answer
    # }

    pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    pre_sheet = pre_sheet.reset_index(drop=True)
    print("pre_sheet",pre_sheet)
    header = pre_sheet.columns
    sheet_L = {}
    for i in range (len(header)):
        sheet_L[header[i]] = pre_sheet[header[i]]
    print(sheet_L)
    #sheet_Q.reset_index()
    #qNum_L = len(sheet["question"])
    return sheet_L

##TODO 個人ＩＤ變數------------------------------------------------
class userVar_L():
    def __init__(self,_id):
        self._id = _id
        self.level_L = 1 # 預設level 1
        self.qNum_L = 10 # 每輪題目數量
        self.star_num_L = 0 #集點
        self.isAsked_L = False #出題與否
        self.isChangingLevel_L = True
        self.isStart_L = False
        self.index_L = 0 #第幾題
        self.isInit_L = True
        self.subindex_L = self.index_L
        self.count_L = 1
        self.data_pho, self.data_word, self.data_sen = getSheet(self.level_L)
        self.sheet_L = editSheet(self.data_pho) 
        self.isWord = False 
        self.word_list = []

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
    if event.message.type == 'text':   
        if(user.isInit_L == True or event.message.text =='?'):
            user.isChangingLevel_L = True
            message = TextSendMessage(text="歡迎來到聽力練習！\n\n在這邊可以選擇適合你的難易度。\n\n題目分為發音、詞彙以及句子，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
            line_bot_api.push_message(user._id, message)
            user.isInit_L=False
        if(user.isChangingLevel_L == True):   
            user.isAsked_L = False
            setlevel_bubble = levelBubble('https://upload.cc/i1/2020/06/08/jhziMK.png','聽力練習','總是聽不懂別人在說什麼嗎?')
            line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
        elif user.isStart_L == True:
            if( user.isAsked_L == False ): 
                user.isAsked_L = True
                QA_bubble = Question(user)
                message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                line_bot_api.reply_message(event.reply_token, message)
##-----------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------
def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar_L(user_ID)
        allUser.append(user)
        print("Alluser",allUser)
    return user 

#回饋判斷
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    user = getUser(event.source.user_id)
    if(user.isChangingLevel_L==True):
        level_bubble = setLevel(event.postback.data,user) 
        message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
        line_bot_api.reply_message(event.reply_token,message) 

    elif(event.postback.data == "start"):  
        user.isStart_L = True
    elif(user.isStart_L == True): 
        if user.isWord == True:
            correctAns = str(user.word_list[user.index_L][2])
        else:
            correctAns = str(user.sheet_L["answer"][user.subindex_L])
        print("correct answer = ",str(user.sheet_L["answer"][user.subindex_L]))
        print("answer user.index_L = ", user.index_L)
        print("answer subuser.index_L = ", user.subindex_L)
        if(user.index_L < user.qNum_L): #做完本輪題庫數目
            #print('user.count_L: ', user.count_L)
            if event.postback.data != correctAns:
                if(user.count_L != 0):
                    user.isStart_L = False
                    wrongBubble = tryagainBubble("請再想想!!", "答案不對哦~你再想想看!", 'start')
                    message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.count_L -= 1
                elif(user.count_L == 0):
                    user.isStart_L = False
                    if(user.index_L == 9):
                        loseBubble = finalBubble('再接再厲！!', '好可惜哦~答案是('+ correctAns +')才對哦!')
                    else:    
                        loseBubble = nextBubble('好可惜哦~答案是('+ correctAns +')才對哦!','再接再厲')
                    message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.count_L = 1
                    user.index_L += 1
                user.isAsked_L = False
            else:
                user.isStart_L = False
                user.star_num_L += user.count_L
                print('正確答案!')
                if(user.count_L == 1):
                    reply = '你好棒!一次就答對了!'
                elif(user.count_L == 0):
                    reply = '好棒哦!你答對了!'
                #print(user.count_L, reply)
                if(user.index_L == 9):
                    reply = '好棒哦!你答對了!'
                    correctBubble = finalBubble('恭喜答對!!','好棒哦!你答對了!')
                else:
                    correctBubble = rightBubble(reply)
                message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                line_bot_api.reply_message(event.reply_token,message)
                #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '恭喜你答對了!給你一個小星星!\n'))
                user.index_L += 1
                if(user.index_L < 10):
                    user.isAsked_L = False
                user.count_L = 1
            print('after user.count_L: ', user.count_L)
            print('after user.index_L: ', user.index_L)
    
    elif(event.postback.data == "end"):
        #print('恭喜你做完這次的聽力練習了!star=',user.star_num_L)
        starBubble = totalStarBubble(user)
        message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
        line_bot_api.reply_message(event.reply_token,message)
        user.isStart_L = False

    elif (event.postback.data == "next"): 
        user.index_L = 0
        user.star_num_L = 0
        #TODO
        user.word_list = []
        print("答題分數顯示完 圖數和分數歸零----",user.index_L,user.star_num_L)
        changelevel_bubble = changeLevelBubble()
        message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
        line_bot_api.reply_message(event.reply_token, message)  

    elif (event.postback.data == "changeLevel"): 
        user.isChangingLevel_L = True

    elif (event.postback.data == "next2"):
        user.isStart_L = True
        user.isAsked_L = True
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
        user.level_L = 1
        myResult = readyBubble(user.level_L)
        user.isChangingLevel_L = False
        
    elif (levelinput=='M'):
        user.level_L = 2
        myResult = readyBubble(user.level_L)    
        user.isChangingLevel_L = False

    elif (levelinput=='H'):
        user.level_L = 3
        myResult = readyBubble(user.level_L)
        user.isChangingLevel_L = False

    else:       
        user.isChangingLevel_L = True
        myResult = "N"

    if user.isChangingLevel_L == False:
        user.data_pho, user.data_word, user.data_sen = getSheet(user.level_L)

    return myResult

def Question(user):
    # global user.subindex_L,user.sheet_L
    print("選完階級！開始出題")
    if user.index_L < 3:
        user.subindex_L = user.index_L
        if user.level_L != 3:
            user.sheet_L = editSheet(user.data_pho)
            QA_bubble = QA.QA_Tail(user.sheet_L,user.index_L,user.index_L)
        else: #高級前三題，題目不同
            print("*****change ～～")
            user.sheet_L = editSheet(user.data_pho)
            QA_bubble = QA.QA_Sentence(user.sheet_L,user.index_L,user.subindex_L,'依據音檔，選出最適當的答案')
    elif user.index_L < 7:
        # user.sheet_L = editSheet(user.data_word)
        # QA_bubble = QA.QA_Word(user.sheet_L,user.index_L,user.subindex_L)
        user.subindex_L = user.index_L - 3
        user.isWord = True
        try:
            print(user.word_list[user.subindex_L])
            QA_bubble = QA.QA_Word(user.index_L, user.word_list[user.subindex_L])
        except: 
            user.sheet_L = getVoc.editSheet(user.data_word)
            q_index, q_chinese, q_english = getVoc.getVoc(user.sheet_L)
            option_english,option_english2 = getVoc.getOption(user.data_word, q_index)
            option, answer = getVoc.getQA(q_english, option_english,option_english2)
            q_audio = getVoc.getAudio(user.sheet_L, q_index)
            templist = [q_audio, option, answer]
            print(templist)
            user.word_list.append(templist)
            print(user.word_list[user.subindex_L])
            QA_bubble = QA.QA_Word(user.index_L, user.word_list[user.subindex_L])
    else:
        user.isWord = False
        user.subindex_L = user.index_L-7
        user.sheet_L = editSheet(user.data_sen) 
        QA_bubble = QA.QA_Sentence(user.sheet_L,user.index_L,user.subindex_L,'選出正確的應對句子')
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
                TextComponent(text="恭喜你獲得了" + str(user.star_num_L) + "顆星星!" , size='xs', align = 'center'),
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