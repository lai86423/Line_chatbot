from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from linebot.models import UnfollowEvent
import sys
import traceback
import numpy as np
import pandas as pd
from googletrans import Translator
from openpyxl import load_workbook
from openpyxl import Workbook
import openpyxl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import QA
import QA_Bubble
import getVoc
import datetime 
import pygsheets
from pydub import AudioSegment
import speech_recognition as sr
import time
import tempfile
from gtts import gTTS
from pygame import mixer
import random
import string
import os

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,user.level_P,point

allUser = [] 
##-----------------------------------------------------------------------------------
##-----------------------------------------------------------------------------------
##解謎  初始抓資料＆資料處理
GDriveJSON = 'JSON.json'
GSpreadSheet_P = 'cilab_ChatBot_puzzle'
gc_Q= pygsheets.authorize(service_account_file='JSON.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1nVIgWGQJRIQtMtZSv1HxyDb5FvthBNc0duN4Rlra8to/edit#gid=1732714016'
sh_P = gc_Q.open(GSpreadSheet_P)
sh_P.worksheet_by_title('d0').export(filename='d0')
sh_P.worksheet_by_title('r0').export(filename='r0')
sheet_d0 = pd.read_csv('d0.csv') #type: <class 'pandas.core.frame.DataFrame'>
sheet_r0 = pd.read_csv('r0.csv') 

##----------------------------------------------------------------------------------
def getSheet_P(level):  
    if(level == 3):
        print("level == 3")
        sh_P.worksheet_by_title('d3').export(filename='d3')
        sh_P.worksheet_by_title('r3').export(filename='r3')
        sheet_d = pd.read_csv('d3.csv')        
        sheet_r = pd.read_csv('r3.csv') 
    elif(level == 2):
        print("level == 2")
        sh_P.worksheet_by_title('d2').export(filename='d2')
        sh_P.worksheet_by_title('r2').export(filename='r2')
        sheet_d = pd.read_csv('d2.csv')
        sheet_r = pd.read_csv('r2.csv')

    else:        
        print("level == 1")
        sh_P.worksheet_by_title('d1').export(filename='d1')
        sh_P.worksheet_by_title('r1').export(filename='r1')
        sheet_d = pd.read_csv('d1.csv')        
        sheet_r = pd.read_csv('r1.csv') 

    return sheet_d, sheet_r

##----------------------------------------------------------------------------------
class userVar():
    def __init__(self,_id):
        self._id = _id
        #QA
        self.data_Voc, self.data_Reading, self.data_Cloze = getSheetQA(1) #預設傳level = 1
        #self.sheet_Q = getVoc.editSheet(self.data_Voc)
        self.isVoc = False 
        self.VocQA = []

        #Listen
        self.data_pho, self.data_word, self.data_sen = getSheet(1)
        #self.sheet_L = self.data_pho
        self.isWord = False 
        self.word_list = []

        #speech
        self.L1_qa = []
        self.L2_qa = []
        self.L3_qa = []
        self.stt_mes = ''
        self.QA_ = []

        #Puzzle
        self.name = '勇者'
        self.next_id = 0
        self.level_P = 1
        self.index_P = 0 #第幾題
        self.isInit_P = True
        self.isChangingLevel_P = False
        self.isChooseHelp = False
        self.isGetSheet_P = False
        self.isLoad_P = False
        self.isPreStory_P = False
        self.isStart_P = False
        self.isAsked_P = False
        self.levelsheet_d = sheet_d0
        self.levelsheet_r = sheet_r0
        self.text_sheet_P = self.data_Cloze
        self.test_type_list = np.zeros(10)
        self.subindex_P = 0
        self.count_P = 2
        self.star_num_P = 0
        self.count_type_P = 2
        self.isPuzzle_P = True  #目前用在判斷是P還是S功能裡的語音辨識題型 

        self.sheet_word_s = []
        self.sheet_sen_s = []
        self.L1_sen_s = []
        self.L2_sen_s = []
        self.L3_sen_s = []

def reset(user):
    #Puzzle
    user.name = '勇者'
    user.next_id = 0
    user.level_P = 1
    user.index_P = 0 #第幾題
    user.isInit_P = True
    user.isChangingLevel_P = False
    user.isChooseHelp = False
    user.isGetSheet_P = False
    user.isLoad_P = False
    user.isPreStory_P = False
    user.isStart_P = False
    user.isAsked_P = False
    user.levelsheet_d = sheet_d0
    user.levelsheet_r = sheet_r0
    user.text_sheet_P = user.data_Cloze
    user.test_type_list = []
    user.subindex_P = 0
    user.count_P = 2
    user.star_num_P = 0
    user.count_type_P = 2
    user.isPuzzle_P = True  #目前用在判斷是P還是S功能裡的語音辨識題型 

    user.sheet_word_s = []
    user.sheet_sen_s = []
    user.L1_sen_s = []
    user.L2_sen_s = []
    user.L3_sen_s = []

# 出題初始抓資料＆資料處理------------------------------------------------
GSpreadSheet_Q = 'cilab_ChatBot_QA'
gc_Q = pygsheets.authorize(service_account_file='JSON.json')
sh_Q = gc_Q.open(GSpreadSheet_Q)
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('JSON.json', scope)
client = gspread.authorize(creds)
spreadSheet = client.open('cilab_ChatBot_QA')
sheet_L1_Cloze = spreadSheet.worksheet("L1_Cloze")
L1_Cloze = sheet_L1_Cloze.get_all_values()
sheet_L2_Cloze = spreadSheet.worksheet("L2_Cloze")
L2_Cloze = sheet_L2_Cloze.get_all_values()
sheet_L3_Cloze = spreadSheet.worksheet("L3_Cloze")
L3_Cloze = sheet_L3_Cloze.get_all_values()

sheet_L1_Reading = spreadSheet.worksheet("L1_Reading")
L1_Reading = sheet_L1_Reading.get_all_values()
sheet_L2_Reading = spreadSheet.worksheet("L2_Reading")
L2_Reading = sheet_L2_Reading.get_all_values()
sheet_L3_Reading = spreadSheet.worksheet("L3_Reading")
L3_Reading = sheet_L3_Reading.get_all_values()
##-----------------------------------------------------------------------------------
def getSheetQA(Qlevel):   
    if(Qlevel == 3):
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze 

    elif(Qlevel == 2):
        sheet_Reading = L2_Reading
        sheet_Cloze = L2_Cloze
    else:
        sheet_Reading = L1_Reading
        sheet_Cloze = L1_Cloze
    
    sheet_Voc = getVoc.getSheet(Qlevel,sh_Q)
    
    return sheet_Voc, sheet_Reading, sheet_Cloze

##---------------------------------------------------------------------------
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc_L = pygsheets.authorize(service_account_file='JSON.json') #檔案裡的google user.sheet_L js檔
sh_L = gc_L.open(GSpreadSheet_L)
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('JSON.json', scope)
client = gspread.authorize(creds)
spreadSheet = client.open('cilab_ChatBot_listening')
sheet_L1_pho = spreadSheet.worksheet("L1_pho")
L1_pho = sheet_L1_pho.get_all_values()
sheet_L2_pho = spreadSheet.worksheet("L2_pho")
L2_pho = sheet_L2_pho.get_all_values()
sheet_L3_pho = spreadSheet.worksheet("L3_pho")
L3_pho = sheet_L3_pho.get_all_values()

sheet_L1_sen = spreadSheet.worksheet("L1_sen")
L1_sen = sheet_L1_sen.get_all_values()
sheet_L2_sen = spreadSheet.worksheet("L2_sen")
L2_sen = sheet_L2_sen.get_all_values()
sheet_L3_sen = spreadSheet.worksheet("L3_sen")
L3_sen = sheet_L3_sen.get_all_values()

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
    
    sheet_word = getVoc.getSheet(Qlevel,sh_L)
    
    return sheet_pho, sheet_word, sheet_sen

#--------------抓題目----------------------------
scope_S = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds_S = ServiceAccountCredentials.from_json_keyfile_name("./speak.json", scope_S)
client_S = gspread.authorize(creds_S)
spreadSheet_S = client_S.open("cilab_ChatBot_speaking")
#random.seed(10)
L1_voc_sheet = spreadSheet_S.worksheet("L1_voc")
L1_voc_data = L1_voc_sheet.get_all_values()
del(L1_voc_data[0])
L1_sen_sheet = spreadSheet_S.worksheet("L1_sen")
L1_sen_data = L1_sen_sheet.get_all_values()
del(L1_sen_data[0])
L2_voc_sheet = spreadSheet_S.worksheet("L1_voc")
L2_voc_data = L2_voc_sheet.get_all_values()
del(L1_voc_data[0])
L2_sen_sheet = spreadSheet_S.worksheet("L2_sen")
L2_sen_data = L2_sen_sheet.get_all_values()
del(L2_sen_data[0])
L3_voc_sheet = spreadSheet_S.worksheet("L3_voc")
L3_voc_data = L3_voc_sheet.get_all_values()
del(L3_voc_data[0])
L3_sen_sheet = spreadSheet_S.worksheet("L3_sen")
L3_sen_data = L3_sen_sheet.get_all_values()
del(L3_sen_data[0])

def getSheet_S(Qlevel, user):   
    user.L1_qa = random.sample(L1_voc_data, 10)
    user.L1_sen_s = random.sample(L1_sen_data, 10)
    #user.L1_qa.extend(random.sample(L1_sen_data, 5))
    user.L2_qa = random.sample(L2_voc_data, 10)
    user.L2_sen_s = random.sample(L2_sen_data, 10)
    #user.L2_qa.extend(random.sample(L2_sen_data, 5))
    user.L3_qa = random.sample(L3_voc_data, 10)
    user.L3_sen_s = random.sample(L3_sen_data, 10)
    #user.L3_qa.extend(random.sample(L3_sen_data, 5))
    
    if(Qlevel == 3):
        user.sheet_word_s = user.L1_qa
        user.sheet_sen_s = user.L1_sen_s
    elif(Qlevel == 2):
        #user.QA_ = user.L2_qa
        user.sheet_word_s = user.L2_qa
        user.sheet_sen_s = user.L2_sen_s
    else:
        #user.QA_ = user.L3_qa
        user.sheet_word_s = user.L3_qa
        user.sheet_sen_s = user.L3_sen_s

##----------------------------------------------------------------------------------

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
    #global user.isInit_P,  user.isAsked_P, user.isLoad_P
    user = getUser(event.source.user_id)
    if event.message.text =='#puzzle':
        reset(user)
        if(user.isInit_P == True):
            user.isInit_P = False
            smallpuzzle(event,'d00000',sheet_d0, user)       
        if user.next_id == 'd00003':
            user.name = event.message.text
            print(event.message.text)
            print(user.name)
            smallpuzzle(event, user.next_id , user.levelsheet_d, user)         
    #---------------------------------------    
            # #------Test
            # user.levelsheet_d, user.levelsheet_r = getSheet_P(1)
            # smallpuzzle(event,'d10029',user.levelsheet_d, user)
            # #------Test
##-----------------------------------------------------------------------------------
def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar(user_ID)
        allUser.append(user)
        print("Alluser",allUser)
    return user 

#回饋判斷
@handler.add(PostbackEvent)
def handle_postback(event):
    user = getUser(event.source.user_id)
    pb_event = event.postback.data
    print("postbackData = ",pb_event )
    
    if (pb_event == 'Next'):
        if user.isGetSheet_P == True:
            user.isGetSheet_P = False
            print("level = ",user.level_P)
            setLevelStory(event, user)

        elif user.isLoad_P == True:
            user.isLoad_P = False
            message = LoadTestIndex(user)
            line_bot_api.reply_message(event.reply_token, message)  
            user.isPreStory_P = True

        elif user.isPreStory_P == True:
            if user.isAsked_P == False :
                print("isPreStory")
                user.isAsked_P = True
                #題前故事
                test_type = user.test_type_list[user.index_P]
                print("test_type = ", test_type)
                print('--TestPreStory--'+'d'+ str(user.level_P) + str(test_type) + '000')
                smallpuzzle(event, 'd' + str(user.level_P) + str(test_type) + '000', user.levelsheet_d, user)
            else:
                smallpuzzle(event, user.next_id , user.levelsheet_d, user)

        elif(user.isStart_P == True):
            print("load_Q")
            bubble = Question_P(event, user)
            message = FlexSendMessage(alt_text="bubble", contents = bubble)
            line_bot_api.reply_message(event.reply_token, message)

        else:
            if(user.next_id != 'd00002'):
                smallpuzzle(event, user.next_id , user.levelsheet_d, user)  

    elif user.isChangingLevel_P == True:
        setLevel_P(pb_event, user)
        #隨機取得題型
        smallpuzzle(event,'d00202',sheet_d0, user)
    
    elif user.isChooseHelp == True:
        #--Game State-----------------------------------
        user.isChooseHelp = False
        if pb_event == '1':
            #了解背景故事
            smallpuzzle(event,'d00100',sheet_d0, user)

        elif pb_event == '2':
            #開始遊戲
            smallpuzzle(event,'d00200',sheet_d0, user)

        elif pb_event == '3':
            #結束遊戲
            print("End!")

        else:
            pass
    elif user.isStart_P == True:
        print("---Ans feedback---")
        if user.isVoc == True:
            correctAns = str(user.VocQA[2])
        elif user.isWord == True:
            correctAns = str(user.word_list[2])
        else:
            correctAns = str(user.text_sheet_P[user.subindex_P][4])
        print("correct answer = ",correctAns)
        print("correct answer, answer user.index_P, subuser.index_P = ",correctAns, user.index_P, user.subindex_P)
        checkAnswer(pb_event, correctAns, user, event)

def checkAnswer(pb_event, correctAns, user, event):
    if pb_event != correctAns:
        print("answer",pb_event," != correctAns",correctAns)
        if(user.count_P != user.count_type_P - 1):
            print("Wrong 1")
            user.isStart_P = False
            user.count_P -= 1
            user.next_id = 'd'+ str(user.level_P) + str(user.test_type_list[user.index_P]) + '200'
            print("nextID",user.next_id)
            smallpuzzle(event, user.next_id, user.levelsheet_d, user)
            
        elif(user.count_P == user.count_type_P - 1):
            user.isStart_P = False
            print("Wrong 2")
            user.next_id = 'd'+ str(user.level_P) + str(user.test_type_list[user.index_P]) + '300'
            print("nextID",user.next_id)
            user.count_P = 2
            smallpuzzle(event, user.next_id, user.levelsheet_d, user)

    else:
        user.isStart_P = False
        user.star_num_P += user.count_P
        print('正確答案!')
        user.next_id = 'd'+ str(user.level_P) + str(user.test_type_list[user.index_P]) + '100'
        print("nextID", user.next_id)
        if(user.count_P == user.count_type_P):
            reply = '你好棒!一次就答對了!'
            print(reply)
            smallpuzzle(event, user.next_id, user.levelsheet_d, user)

        elif(user.count_P == user.count_type_P - 1):
            reply = '好棒哦!你答對了!'
            print(reply)
            smallpuzzle(event, user.next_id, user.levelsheet_d, user)

        user.count_P = 2 
    print('after count_P: ', user.count_P)
    #print('after index_P: ', user.index_P)
##-----------------------------------------------------------------------------------
def setLevel_P(levelinput, user):
    print("---Changing Level---")
    #global user.level_P, user.isChangingLevel_P

    if (levelinput=='L'):
        user.level_P = 1
        user.isChangingLevel_P = False
        
    elif (levelinput=='M'):
        user.level_P = 2
        user.isChangingLevel_P = False

    elif (levelinput=='H'):
        user.level_P = 3
        user.isChangingLevel_P = False

    else:       
        user.isChangingLevel_P = True

def smallpuzzle(event,id, sheet, user):
    print("---------id----------",id)
    id_index = sheet["a-descriptionID"].index[sheet["a-descriptionID"] == id] 

    #print("#####",id_index) 
    if len(id_index) > 0:
        id_index = id_index[0]
        print("id_index",id_index)

        user.next_id = id[0:3]+ str( int(id[3:6]) + 1).zfill(3)
        print("next id = ", user.next_id)

        sheet_type = sheet["type"][id_index]
        print("sheet_type",sheet_type)
        
        if sheet_type == 'image':   
            sheet_text = sheet["text"][id_index]  
            print("img= ",sheet_text)  
            message = ImageBubble(sheet_text)
            line_bot_api.reply_message(event.reply_token, message)                  
            #smallpuzzle(event, user.next_id , sheet, user)

        elif sheet_type == 'text':
            sheet_text = sheet["text"][id_index]
            if '$username' in sheet_text:   # 使用in運算子檢查
                sheet_text = sheet_text.replace('$username', user.name)
                print('字串中有\'$username\'')
            print("text= ",sheet_text)
            message = TextBubble(sheet_text)
            line_bot_api.reply_message(event.reply_token, message)  

        elif sheet_type == 'button': 
            if id == 'd00003':
                user.isChooseHelp = True
            if id == 'd00201':
                user.isChangingLevel_P = True
            sheet_title = sheet["title"][id_index]
            sheet_text = sheet["text"][id_index]
            sheet_reply_list = []
            for i in range (3):
                if (str(sheet.iloc[id_index][4 + i]) != "") : 
                    sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))

            replylist = ButtonPuzzle(sheet_reply_list)
            button_bubble = ButtonBubble(sheet_title, sheet_text, replylist)
            line_bot_api.reply_message(event.reply_token, button_bubble)  
        
        elif sheet_type == 'confirm':
            sheet_text = sheet["text"][id_index]
            sheet_reply_list = []
            for i in range (2):
                if (str(sheet.iloc[id_index][4 + i]) != "") : 
                    sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))
            print("Cofirm sheet_reply_list",sheet_reply_list)
            replylist = CofirmPuzzle(sheet_reply_list, user)
            print("Cofirm replylist",replylist)
            confirm_bubble = ConfirmBubble(sheet_text, replylist)
            line_bot_api.reply_message(event.reply_token, confirm_bubble)
        elif sheet_type == 'input':
            sheet_text = sheet["text"][id_index]
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = sheet_text)) 

    else:
        print("Do Not Find ID in Sheet! ")
        if id =='d00102': #重複詢問可以幫您什麼？
            smallpuzzle(event,'d00003',sheet_d0, user)
        
        elif id =='d00208':
            print("isGetSheet")
            user.levelsheet_d, user.levelsheet_r = getSheet_P(user.level_P)
            user.data_pho, user.data_word, user.data_sen = getSheet(user.level_P)
            user.data_Voc, user.data_Reading, user.data_Cloze = getSheetQA(user.level_P) #預設傳level = 1
            getSheet_S(user.level_P, user)
            user.isGetSheet_P = True
        
        #---------------------------------------------------

        #剛開始答題
        elif id == 'd10030' or id == 'd20025' or id == 'd30022':
            RandomTest(user)
            user.isLoad_P = True
        elif (int(id[1:2]) == (user.level_P)):#非d0表單
            if(int(id[2:3]) == (user.test_type_list[user.index_P])):  
                #答對
                if id[3:4] == '1': 
                    if  user.index_P < 5:
                        print("答對 繼續isLoad_P")
                        user.index_P += 1
                        user.isLoad_P = True
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
                #第一次答錯
                elif id[3:4] == '2':
                    if user.index_P < 5:
                        print("第一次答錯 再一次 isStart_P，Load題目")
                        user.isStart_P = True
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
                #第二次答錯
                elif id[3:4] == '3':
                    if user.index_P < 5:
                        user.index_P += 1
                        user.isLoad_P = True
                        print("第二次答錯 新題目PreStory")
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
            #---------------------------------------------------  
            #----計算最後答題結果
            #是否大於六題
            elif id[2:4] == '01':
                if user.star_num_P >= 3:
                    smallpuzzle(event,'d'+ str(user.level_P) + '0200', user.levelsheet_d, user)
                else:
                    smallpuzzle(event,'d'+ str(user.level_P) + '0300', user.levelsheet_d, user)
            #結尾故事
            elif id[2:4] == '02' or id[2:4] == '03':
                    smallpuzzle(event,'d'+ str(user.level_P) + '0400', user.levelsheet_d, user)

            #結束 回到最初功能選擇
            elif id[2:4] == '04':
                    smallpuzzle(event,'d00003',sheet_d0, user)

            if user.isPreStory_P == True:
                print("PreStory End! Strat Testing!")
                user.isStart_P = True
                user.isAsked_P = False
                user.isPreStory_P = False
        
        pass

def ButtonPuzzle(sheet_reply_list):
    replylist = []
    print("ButtonPuzzle",sheet_reply_list)
    for i in range(len(sheet_reply_list)):
        id_index = sheet_r0["a-replyID"].index[sheet_r0["a-replyID"] == sheet_reply_list[i]]
        replylist.append(([sheet_r0["label"][id_index[0]], sheet_r0["text"][id_index[0]], sheet_r0["data"][id_index[0]]]))
    print("replylist",replylist) 
    return replylist

def CofirmPuzzle(sheet_reply_list, user):
    print("CofirmBubble",sheet_reply_list)
    replylist = []
    for i in range(len(sheet_reply_list)):
        id_index = user.levelsheet_r["a-replyID"].index[user.levelsheet_r["a-replyID"] == sheet_reply_list[i]]
        replylist.append(([user.levelsheet_r["label"][id_index[0]], user.levelsheet_r["text"][id_index[0]], user.levelsheet_r["data"][id_index[0]]]))
    print("--Cofirm replylist",replylist) 
    return replylist

def setLevelStory(event, user):
    print("setLevelStory")

    if user.level_P == 1:
        smallpuzzle(event,'d10000' , user.levelsheet_d, user)

    elif user.level_P == 2:
        smallpuzzle(event,'d20000' , user.levelsheet_d, user)

    elif user.level_P == 3:
        smallpuzzle(event,'d30000' , user.levelsheet_d, user)

def RandomTest(user):
    #global user.test_type_list
    user.test_type_list = [random.randint(1,7) for _ in range(10)]
    print("-----*** 5 Quiz type = ",user.test_type_list)

def LoadTestIndex(user):
    print("-----LoadTestIndex----", user.index_P)
    #題數引文
    if user.level_P == 1 :
        test_pretext = "（第" + str(user.index_P+1) + " 題）\n【Silas】：\n勇者$username ，現在是 "+ str(8+user.index_P) +":00，Ariel 希望我們在傍晚18:00前完成。"
        print(test_pretext)
        message = TextBubble(test_pretext)
        #line_bot_api.push_message(_id, message)
    
    elif user.level_P == 2:
        test_pretext = "（第" + str(user.index_P+1) + " 題）\n【Keith】：\n勇者$username ，現在是 "+ str(8+user.index_P) +":00，Faun 希望我們在傍晚18:00前完成。"
        print(test_pretext)
        message = TextBubble(test_pretext)

    elif user.level_P == 3:
        test_pretext = "（第" + str(user.index_P+1) + " 題）\n【Cynthia】：\n真是太好了！剛好每天晚上Helena都會在他的閣樓唱歌給大家聽，我們趕緊去找，18:00拿去給領主吧！\n勇者，Let's go！"
        print(test_pretext)
        message = TextBubble(test_pretext)
    return message

def Question_P(event, user):
    user.isVoc = False
    user.isWord = False
    user.count_type_P = 2
    
    if user.test_type_list[user.index_P] == 1:

        print("sheet_L_pho & word")
        #test_type1 = random.randint(1, 2)
        test_type1 = 2
        if test_type1 == 1:
            print("--sheet_pho--")
            if user.level_P != 3:
                user.count_type_P = 1
                
                if user.count_P == 2:
                    user.count_P = 1
                
                if user.count_P == user.count_type_P:
                    print("random QA_Tail subindex")
                    #---test 用 之後前面有跑setLevel即可拿掉
                    user.data_pho, user.data_word, user.data_sen = getSheet(user.level_P)
                    #---
                    user.text_sheet_P = user.data_pho
                    user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0]))
                user.text_sheet_P = user.data_pho
                bubble = QA.QA_Tail(user.text_sheet_P,user.index_P,user.subindex_P)
            else: #高級前三題，題目不同
                print("---level 3 pho  依據音檔選句子---")
                if user.count_P == user.count_type_P :
                    #---test後拿掉----
                    user.data_pho, user.data_word, user.data_sen = getSheet(3)
                    #---test後拿掉----
                    user.text_sheet_P = user.data_pho
                    user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0]))
                bubble = QA.QA_Sentence(user.text_sheet_P,user.index_P,user.subindex_P,'依據音檔，選出最適當的答案')
        else:
            print("--sheet_word--",test_type1)
            user.isWord = True
            if user.count_P == user.count_type_P:
                user.text_sheet_P = getVoc.editSheet(user.data_word)
                q_index, q_chinese, q_english = getVoc.getVoc(user.text_sheet_P)
                option_english,option_english2 = getVoc.getOption(user.data_word, q_index)
                option, answer = getVoc.getQA(q_english, option_english,option_english2)
                q_audio = getVoc.getAudio(user.text_sheet_P, q_index)
                user.word_list = [q_audio, option, answer]
            print("user.word_list",user.word_list)
            bubble = QA.QA_Word(user.index_P, user.word_list)
    
    elif user.test_type_list[user.index_P] == 2:
        print("sheet_L_sen")
        #---test 用 之後前面有跑setLevel即可拿tt掉
        #user.data_pho, user.data_word, user.data_sen = getSheet(user.level_P)
        #---
        user.text_sheet_P = user.data_sen
        if user.count_P == user.count_type_P :
            print("random subindex_P")
            user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0])) 
        print("user.subindex_P",user.subindex_P)
        bubble = QA.QA_Sentence(user.text_sheet_P,user.index_P,user.subindex_P,'選出正確的應對句子')
    
    elif user.test_type_list[user.index_P] == 3:
        print("sheet_speaking_word")
        #---test 用 之後前面有跑setLevel即可拿tt掉
        # if user.count_P == user.count_type_P :
        #     getSheet_S(user.level_P, user)
        #---test 用 之後前面有跑setLevel即可拿tt掉
        bubble = QA_S(user.sheet_word_s[user.index_P][0], user.sheet_word_s[user.index_P][1], user, user.index_P)

    elif user.test_type_list[user.index_P] == 4:
        print("sheet_speaking_sen")
        #---test 用 之後前面有跑setLevel即可拿tt掉
        # if user.count_P == user.count_type_P :
        #     getSheet_S(user.level_P, user)
        #---test 用 之後前面有跑setLevel即可拿tt掉
        bubble = QA_S(user.sheet_sen_s[user.index_P][0], user.sheet_sen_s[user.index_P][1], user, user.index_P)

    elif user.test_type_list[user.index_P] == 5:
        print("sheet_Q_voc")
        user.isVoc = True
        if user.count_P == user.count_type_P:
            user.text_sheet_P = getVoc.editSheet(user.data_Voc)
            q_index, q_chinese, q_english = getVoc.getVoc(user.text_sheet_P)
            option_english,option_english2 = getVoc.getOption(user.data_Voc, q_index)
            option, answer = getVoc.getQA(q_english, option_english,option_english2)
            user.VocQA = [q_chinese, option, answer]
        print(user.VocQA)
        bubble = QA_Bubble.Voc(user.index_P, user.VocQA)

    elif user.test_type_list[user.index_P] == 6:
        print("sheet_Q_cloze")
        user.text_sheet_P = user.data_Cloze
        if user.count_P == user.count_type_P:
            user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0]))
            print("data_Cloze subindex_P", user.subindex_P)
        if (user.level_P != 3):
            bubble = QA_Bubble.Cloze(user.text_sheet_P, user.index_P, user.subindex_P)
        else:
            bubble = QA_Bubble.Cloze_L3(user.text_sheet_P, user.index_P, user.subindex_P)

    elif user.test_type_list[user.index_P] == 7:
        print("sheet_Q_reading")
        #---test 用 之後前面有跑setLevel即可拿掉
        #user.data_Voc, user.data_Reading, user.data_Cloze = getSheetQA(user.level_P) 
        #---
        if(user.count_P == user.count_type_P):
            user.text_sheet_P = user.data_Reading
            print("reading", len( np.transpose( [user.text_sheet_P])[0] ) )
            user.subindex_P = random.randrange(1, len(np.transpose([user.text_sheet_P])[0]), 3)
            QA_bubble_article = QA_Bubble.Article( user.text_sheet_P, user.subindex_P )
            article = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble_article)
            line_bot_api.push_message(event.source.user_id, article)
        
        bubble = QA_Bubble.Reading(user.data_Reading, user.index_P, user.subindex_P)
                                                                                                                                                                         
    return bubble

#------------語音處理訊息----------------
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    print("AudioMessage")
    user = getUser(event.source.user_id)
    r = sr.Recognizer()
    message_content = line_bot_api.get_message_content(event.message.id)
    ext = 'mp3'
    try:
        with tempfile.NamedTemporaryFile(prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        path = tempfile_path 
        AudioSegment.converter = '/app/vendor/ffmpeg/ffmpeg'
        sound = AudioSegment.from_file_using_temporary_files(path)
        path = os.path.splitext(path)[0]+'.wav'
        sound.export(path, format="wav")
        with sr.AudioFile(path) as source:
            audio = r.record(source)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")

    except sr.RequestError as e:
        if user.isPuzzle_P == True:
            checkAnswer('1', '2', user, event)
            
        else:
            print("user.isPuzzle_P = False!!")
            # if(user.count_P != 1):
            #     wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain','')
            #     message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
            #     line_bot_api.reply_message(event.reply_token,message)
            #     user.count_S -= 1
            # elif(user.count_S == 1):
            #         if(user.index_S == 9):
            #             loseBubble = finalBubble('再接再厲!!', '好可惜哦!\n往上滑再聽一次正確發音吧!', user.stt_mes)
            #         else:
            #             loseBubble = loseBubble = nextBubble('好可惜哦!\n往上滑再聽一次正確發音吧!','再接再厲!!',user.stt_mes)
            #         message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
            #         line_bot_api.reply_message(event.reply_token,message)
            #         user.count_S = 2
            #         user.index_S += 1            
    except Exception as e:
        if user.isPuzzle_P == True:
            checkAnswer('1', '2', user, event)

        else:
            print("user.isPuzzle_P = False!!")
            # t = '音訊有問題'+test+str(e.args)+path
            # wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain','')
            # message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
            # line_bot_api.reply_message(event.reply_token,message)
    
    os.remove(path)
    text = r.recognize_google(audio,language='zh-En')
    user.stt_mes = text
    print('原始語音訊息：', user.stt_mes)
    user.stt_mes = user.stt_mes.lower()

    print('忽略大小寫語音訊息：', user.stt_mes)
    #exclude = set(string.punctuation)
    exclude = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + '‘’→↓△▿⋄•！？?〞＃＄％＆』（）＊＋，－╱︰；＜＝＞＠〔╲〕 ＿ˋ｛∣｝∼、〃》「」『』【】﹝﹞【】〝〞–—『』「」…﹏'
    output_mes = ''.join(ch for ch in user.stt_mes if ch not in exclude)

    if user.isPuzzle_P == True:
        if user.test_type_list[user.index_P] == 3:
            user.sheet_word_s[user.index_P][1] = user.sheet_word_s[user.index_P][1].lower()
            output_ans = ''.join(se for se in user.sheet_word_s[user.index_P][1] if se not in exclude)
            print('語音處理 sheet_word_s[index_P][1]', user.sheet_word_s[user.index_P][1])

        elif user.test_type_list[user.index_P] == 4:
            user.sheet_sen_s[user.index_P][1] = user.sheet_sen_s[user.index_P][1].lower() 
            output_ans = ''.join(se for se in user.sheet_sen_s[user.index_P][1] if se not in exclude)
            print('語音處理 sheet_sen_s[index_P][1]', user.sheet_sen_s[user.index_P][1])
    else:
        print("user.isPuzzle_P = False!!")
        output_ans = '@@@'
        #user.QA_[user.index_S][1] = user.QA_[user.index_S][1].lower()
        #output_ans = ''.join(se for se in user.QA_[user.index_S][1] if se not in exclude)
        #print('語音處理 QA_[index_S][1]', user.QA_[user.index_S][1])

    print('忽略符號語音訊息：', output_mes)
    print('忽略符號解答：', output_ans)

    if user.isPuzzle_P == True:
        print("!!---speech checkAnswer---!!")
        checkAnswer(output_mes, output_ans, user, event)
    else:
        print("user.isPuzzle_P = False!!")
    # if(output_mes != output_ans):
    #     if(user.count_S != 1):
    #         wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain', user.stt_mes)
    #         message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
    #         line_bot_api.reply_message(event.reply_token,message)
    #         user.count_S -= 1
    #     elif(user.count_S == 1):
    #         if(user.index_S == 9):
    #             loseBubble = finalBubble('再接再厲!!', '好可惜哦!\n往上滑再聽一次正確發音吧!', user.stt_mes)
    #         else:
    #             loseBubble = loseBubble = nextBubble('好可惜哦!\n往上滑再聽一次正確發音吧!','再接再厲!!',user.stt_mes)
    #         message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
    #         line_bot_api.reply_message(event.reply_token,message)
    #         user.count_S = 2
    #         user.index_S += 1
    # else:
    #     user.star_num_s += user.count_S
    #     if(user.count_S == 2):
    #         reply = '你好棒!一次就答對了!'
    #     elif(user.count_S == 1):
    #         reply = '好棒哦!你答對了!'
    #     print(user.count_S, reply)
    #     if(user.index_S == 9):
    #         reply = '好棒哦!你答對了!'
    #         correctBubble = finalBubble('恭喜答對!!', reply, user.stt_mes)
    #         #user_sheet.update_cell(user.index, 8, 1)
    #     else:
    #         correctBubble = rightBubble(reply)
    #     message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
    #     line_bot_api.reply_message(event.reply_token,message)
    #     user.index_S += 1
    #     user.count_S = 2
#-----------------語音處理訊息結束----------------

def ButtonBubble(sheet_title, sheet_text, replylist):
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = sheet_title,
                        text = sheet_text,
                        actions = [
                                PostbackTemplateAction(
                                    label = replylist[0][0], 
                                    text = replylist[0][1],
                                    data = replylist[0][2]
                                ),
                                PostbackTemplateAction(
                                    label = replylist[1][0], 
                                    text = replylist[1][1],
                                    data = replylist[1][2]
                                ),
                                PostbackTemplateAction(
                                    label = replylist[2][0], 
                                    text = replylist[2][1],
                                    data = replylist[2][2]
                                )
                        ]
                    )
                )
    return level_template

def TextBubble(sheet_text):
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        text = sheet_text,
                        actions = [
                                PostbackTemplateAction(
                                    label = "Next", 
                                    data = "Next"
                                )
                        ]
                    )
                )
    return level_template

def ImageBubble(sheet_text):
    level_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        text = ' ',
                        thumbnail_image_url=sheet_text,
                        actions = [
                                PostbackTemplateAction(
                                    label = "Next", 
                                    data = "Next"
                                )
                        ]
                    )
                )
    return level_template

def ConfirmBubble(sheet_text, replylist):
    Confirm_template = TemplateSendMessage(
            alt_text='Confirm_template',
            template=ConfirmTemplate(
                text=sheet_text,
                actions=[                              
                    PostbackTemplateAction(
                                    label = replylist[0][0], 
                                    text = replylist[0][1],
                                    data = replylist[0][2]
                    ),
                    PostbackTemplateAction(
                                    label = replylist[1][0], 
                                    text = replylist[1][1],
                                    data = replylist[1][2]
                    )      
                ]
            )
        )
    return Confirm_template

#-----------------發音Function------------
#TODO index_s 改 傳入～～～！
def QA_S(address, ques, user, index):
    QA_Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="發音練習("+ str(index+1) +"/10)", weight='bold', size='lg', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= ques, weight='bold', size='xl', align = 'center', wrap = True),
                TextComponent(text='請透過語音訊息唸給我聽', margin= 'none',size='sm', align = 'center',gravity = 'center', color= '#727272'),
                SeparatorComponent(margin='xl',color='#A89F9F'),
                ButtonComponent(
                    action = URIAction(label= '聽正確發音', uri= address),
                    color = '#3B9A9C',
                    margin = 'lg',
                    style = 'primary',
                    flex = 10
                )
            ]
        )
    )                       
    return QA_Bubble
##  End------------------------------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)