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

#書
# line_bot_api = LineBotApi('Ay6xk+FmKxu4tFPtdzXBMR/V8Mf1GnwNi07Vt9QgOHCHwUCd3x8pdRMu7rTHR1/QWlcVcaaHRzfi9gARYXgNqm7WT7M7YoeWJv+NFkl+iZg5K0jAERYZud6HpNmpVXm6TEIf7ZY1DxnH55E77umPawdB04t89/1O/w1cDnyilFU=')

# handler = WebhookHandler('533dbc0dab0d92eea7a87b05cb7e49a6')

#映
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#-------功能變數--------
trans = False
quiz = False
listen = False
stt = False
grade = False
#------------------
#-------抓user_id------
user_data = []
check_user = False
check = False
qa_score = 0
lis_score = 0
trans_score = 0
speech_score = 0
game_score = 0
function_status = ''
allUser = []
#----------------------變數------------------------------------------------
#TODO --------------------------------------------
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
sh_P.worksheet_by_title('d1').export(filename='d1')
sh_P.worksheet_by_title('r1').export(filename='r1')
sheet_d1 = pd.read_csv('d1.csv')        
sheet_r1 = pd.read_csv('r1.csv') 
sh_P.worksheet_by_title('d2').export(filename='d2')
sh_P.worksheet_by_title('r2').export(filename='r2')
sheet_d2 = pd.read_csv('d2.csv')        
sheet_r2 = pd.read_csv('r2.csv') 
sh_P.worksheet_by_title('d3').export(filename='d3')
sh_P.worksheet_by_title('r3').export(filename='r3')
sheet_d3 = pd.read_csv('d3.csv')        
sheet_r3 = pd.read_csv('r3.csv') 
##----------------------------------------------------------------------------------
def getSheet_P(level):  
    if(level == 3):
        print("level == 3")
        sheet_d = sheet_d3
        sheet_r = sheet_r3
    elif(level == 2):
        print("level == 2")
        sheet_d = sheet_d2
        sheet_r = sheet_r2

    else:        
        print("level == 1")
        sheet_d = sheet_d1
        sheet_r = sheet_r1

    return sheet_d, sheet_r
#TODO END-------------------------------------
class userVar():
    def __init__(self,_id):
        self._id = _id
        self.score = 0
        self.qa_score = 0
        self.lis_score = 0
        self.trans_score = 0
        self.speech_score = 0
        self.game_score = 0
        self.function_status = ''
        self.data_row = 0
        self.index = 0
        self.check_user = False
        #QA
        self.level_Q = 1 # 預設level 1
        self.qNum_Q = 10 # 每輪題目數量
        self.star_num_Q = 0 #集點
        self.isAsked_Q = False #出題與否
        self.isChangingLevel_Q = True
        self.isStart_Q = False
        self.index_Q = 0 #第幾題
        self.isInit_Q = True
        self.subindex_Q = self.index_Q
        self.count_Q = 2
        self.data_Voc, self.data_Reading, self.data_Cloze = getSheetQA(self.level_Q) #預設傳level = 1
        self.sheet_Q = getVoc.editSheet(self.data_Voc)
        self.isVoc = False 
        self.VocQA = []
        #Listen
        self.level_L = 1 # 預設level 1
        self.qNum_L = 10 # 每輪題目數量
        self.star_num_L = 0 #集點
        self.isAsked_L = False #出題與否
        self.isChangingLevel_L = True
        self.isStart_L = False
        self.index_L = 0 #第幾題
        self.isInit_L = True
        self.subindex_L = self.index_L 
        self.data_pho, self.data_word, self.data_sen = getSheet(self.level_L)
        self.sheet_L = self.data_pho
        self.isWord = False 
        self.word_list = []
        self.count_type_L = 1
        self.count_L = self.count_type_L
        #speech
        self.start_s = 1
        self.star_num_s = 0
        self.index_S = 0
        self.count_S = 2
        self.qNum_S = 10
        self.L1_qa = []
        self.L2_qa = []
        self.L3_qa = []
        self.speech = False
        self.stt_mes = ''
        self.QA_ = []
        self.level = ''
        #Trans
        self.isAsked_T = True
        self.isChangingTrans = True
        self.isEnded = False
        self.TransType = 1
        self.isInit_T = True

        self.isOtherText = False
         #TODO -------------------------------------
        self.name = '???'
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
#TODO END-------------------------------------

#TODO -------------------------------------
def reset_P(user):
    #Puzzle
    user.name = '???'
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
    user.test_type_list = np.zeros(10)
    user.subindex_P = 0
    user.count_P = 2
    user.star_num_P = 0
    user.count_type_P = 2
    user.isPuzzle_P = True  #目前用在判斷是P還是S功能裡的語音辨識題型 

#TODO END-------------------------------------

##-----------------------------------------------------------------------------------
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
##----------------------------------------------------------------------------------
#三種問題類型
def getSheet(Qlevel):   
    if(Qlevel == 3):
        sheet_pho = L3_pho
        sheet_sen = L3_sen  

    elif(Qlevel == 2):
        sheet_pho = L2_pho
        sheet_sen = L2_sen 
    else:
        sheet_pho = L1_pho
        sheet_sen = L1_sen 
    
    sheet_word = getVoc.getSheet(Qlevel,sh_L)
    
    return sheet_pho, sheet_word, sheet_sen

##---------------------------------------------------------------------------
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

##----------------------------------------------------------------------------------

#三種問題類型
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

#------翻譯變數----------------------------
isAsked_T = True
isChangingTrans = True
isEnded = False
TransType = 1 #(ETC= 1, CTE =2)
#---------------user_score------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
client = gspread.authorize(creds)
spreadSheet = client.open("user_score")
user_sheet = spreadSheet.worksheet("user_score")
user_data = user_sheet.get_all_values()
print('!!!!!!!!!!!!!!!!!!user:', user_data)

##------------------------------------------------
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
L2_voc_sheet = spreadSheet_S.worksheet("L2_voc")
L2_voc_data = L2_voc_sheet.get_all_values()
del(L2_voc_data[0])
L2_sen_sheet = spreadSheet_S.worksheet("L2_sen")
L2_sen_data = L2_sen_sheet.get_all_values()
del(L2_sen_data[0])
L3_voc_sheet = spreadSheet_S.worksheet("L3_voc")
L3_voc_data = L3_voc_sheet.get_all_values()
del(L3_voc_data[0])
L3_sen_sheet = spreadSheet_S.worksheet("L3_sen")
L3_sen_data = L3_sen_sheet.get_all_values()
del(L3_sen_data[0])
#-------------------查看積分變數-------------------
check_grade = True
choose = '0'
#TODO -------------------------------------
def getSheet_S(Qlevel, user):   
    user.L1_qa = random.sample(L1_voc_data, 10)
    user.L1_sen_s = random.sample(L1_sen_data, 10)
    user.L2_qa = random.sample(L2_voc_data, 10)
    user.L2_sen_s = random.sample(L2_sen_data, 10)
    user.L3_qa = random.sample(L3_voc_data, 10)
    user.L3_sen_s = random.sample(L3_sen_data, 10)
    
    if(Qlevel == 3):
        user.sheet_word_s = user.L1_qa
        user.sheet_sen_s = user.L1_sen_s
    elif(Qlevel == 2):
        user.sheet_word_s = user.L2_qa
        user.sheet_sen_s = user.L2_sen_s
    else:
        user.sheet_word_s = user.L3_qa
        user.sheet_sen_s = user.L3_sen_s
#TODO END-------------------------------------

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
#-------unfollow event---------
@handler.add(UnfollowEvent)
def handle_follow(event):
    check = False
    index_u = 0
    user_data = user_sheet.get_all_values()
    for i in range(1,len(user_data)):
        if (user_data[i][0] == event.source.user_id):
            check = True
            index_u = i + 1
            break
    if (check == True):
        user_sheet.delete_row(index_u)
#----------處理訊息--------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_data
    global user_sheet
    user = getUser(event.source.user_id)
    user_data = user_sheet.get_all_values()
    #print('!!!!!!!!!!!!!!!!!!user:', user_data)
    for i in range(1,len(user_data)):
        #print('user_data[i][0]:',user_data[i][0])
        #print('id:', event.source.user_id)
        #print('user_data[i][0]:',user_data[i][1])
        if (user_data[i][0] == event.source.user_id):
            user.check_user = True
            user.index = i + 1
            #print('find user!!!!')
            break
    #print('check_user: ', check_user)
    if (user.check_user == False):
        user.index = len(user_data) + 1
        user_sheet.add_rows(1)
        user_sheet.update_cell(user.index, 1, event.source.user_id)
        user_sheet.update_cell(user.index, 2, 'null')
        user_sheet.update_cell(user.index, 3, '0')
        user_sheet.update_cell(user.index, 4, '0')
        user_sheet.update_cell(user.index, 5, '0')
        user_sheet.update_cell(user.index, 6, '0')
        user_sheet.update_cell(user.index, 7, '0')
        user_data.append([event.source.user_id, 'null', 0, 0, 0, 0, 0,])
    user.data_row = user.index - 1
    user.function_status = user_data[user.data_row][1]
    user.score = int(user_data[user.data_row][2])
    user.qa_score = int(user_data[user.data_row][3])
    user.lis_score = int(user_data[user.data_row][4])
    user.speech_score = int(user_data[user.data_row][5])
    user.game_score = int(user_data[user.data_row][6])
    check_user = False
    ############################################
    if event.message.type == 'text':
        if(event.message.text == '#translation'):
            reset(user)
            user.function_status = 'translation'
            user_data[user.data_row][1] = 'translation'
            user_sheet.update_cell(user.index, 2, 'translation')
            print('translation trans True')
        elif(event.message.text == '#quiz'):
            reset(user)
            user.function_status = 'quiz'
            user_data[user.data_row][1] = 'quiz'
            user_sheet.update_cell(user.index, 2, 'quiz')
            print('quiz trans True')
        elif(event.message.text == '#listen'):
            reset(user)
            user.function_status = 'listen'
            user_data[user.data_row][1] = 'listen'
            user_sheet.update_cell(user.index, 2, 'listen')
            print('listen trans True')
        elif(event.message.text == '#speech'):
            user.function_status = 'speech'
            reset(user)
            reset_s(user)
            user_data[user.data_row][1] = 'speech'
            user_sheet.update_cell(user.index, 2, 'speech')
            print('stt trans True')
        elif(event.message.text == '#score'):
            reset(user)
            user.function_status = 'score'
            user_data[user.data_row][1] = 'score'
            user_sheet.update_cell(user.index, 2, 'score')
            print('grade trans True')
        elif(event.message.text == '#game'):
            reset(user)
            reset_P(user)
            user.function_status = 'game'
            user_data[user.data_row][1] = 'game'
            user_sheet.update_cell(user.index, 2, 'game')
            print('game trans True')
        
        user.function_status = user_data[user.data_row][1]
        print('!!!!!-------status--------!!!!!: ', user.function_status)
    #-----------出題處理訊息-----------------
        if(user.function_status == 'quiz'):
            replytext = event.message.text
            myId = event.source.user_id
            reset_s(user)
            if event.message.type == 'text':   
                if(user.isInit_Q == True):
                    user.isChangingLevel_Q = True
                    message = TextSendMessage(text="歡迎來到解題小達人！\n\n在這邊可以選擇適合你的難易度來挑戰，一組題目有10題。\n\n題目分為詞彙題、克漏字以及閱讀測驗，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
                    line_bot_api.push_message(user._id, message)
                    user.isInit_Q = False

                if(user.isChangingLevel_Q == True):   
                    if user.isOthertext == False: 
                        user.isAsked_Q = False
                        setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/V5TmMA.png','解題小達人', '總是聽不懂別人在說什麼嗎?')
                        line_bot_api.reply_message(event.reply_token, setlevel_bubble) 
                        user.isOthertext = True
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="咦？我不知道你在說什麼"))
 
                elif user.isStart_Q == True:
                    if( user.isAsked_Q == False): 
                        user.isAsked_Q = True
                        QA_bubble = Question_Q(user)
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
                    #else:
                    #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="咦？我不知道你在說什麼"))
     
#--------------聽力處理訊息--------------------
        elif(user.function_status == 'listen'):
            reset_s(user)
            replytext = event.message.text
            myId = event.source.user_id
            if event.message.type == 'text':   
                if(user.isInit_L == True):
                    user.isChangingLevel_L = True
                    message = TextSendMessage(text="歡迎來到聽力練習！\n\n在這邊可以選擇適合你的難易度。\n\n題目分為發音、詞彙以及句子，答題越精確獲得的星星數越多哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
                    line_bot_api.push_message(user._id, message)
                    user.isInit_L=False
                if(user.isChangingLevel_L == True):   
                    if user.isOthertext == False: 
                        user.isAsked_L = False
                        setlevel_bubble = levelBubble('https://upload.cc/i1/2020/06/08/jhziMK.png','聽力練習','總是聽不懂別人在說什麼嗎?')
                        line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
                        user.isOthertext = True
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="咦？我不知道你在說什麼"))
     
                elif user.isStart_L == True:
                    if( user.isAsked_L == False ): 
                        user.isAsked_L = True
                        QA_bubble = Question(user)
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
                        
                    #else:
                    #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="咦？我不知道你在說什麼"))
  
#----------------翻譯處理訊息---------------
        elif(user.function_status == 'translation'):
            myId = event.source.user_id
            reset_s(user)
            replytext = event.message.text
            if event.message.type == 'text':
                if(user.isInit_T == True):
                    user.isChangingTrans = True
                    user.isEnded = False
                    user.isInit_T = False
                if (user.isChangingTrans == True ):  
                    user.isAsked_T = True
                    user.isEnded = False
                    buttons_template = TemplateSendMessage (
                        alt_text = 'Buttons Template',
                        template = ButtonsTemplate (
                            title = '翻譯小達人',
                            text = '有什麼要我幫忙翻譯的嗎?',
                            thumbnail_image_url='https://upload.cc/i1/2020/07/01/IV2yHq.png',
                            actions = [
                                    PostbackTemplateAction(
                                        label = "英文翻中文", 
                                        #text = "英文翻中文",
                                        data = 'ETC'
                                    ),
                                    PostbackTemplateAction(
                                        label = "中文翻英文",
                                        #text = "中文翻英文",
                                        data = 'CTE'
                                    )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, buttons_template)
                    
                elif(user.isAsked_T == False ):  
                    translatedMessage = translation(replytext, user)
                    print("tenasM = ",translatedMessage)
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = translatedMessage))

                    Translation_bubble = Choose_NextStep()
                    message2 = FlexSendMessage(alt_text="Translation_bubble", contents = Translation_bubble)
                    line_bot_api.push_message(myId, message2)
                    user.isAsked_T = True 
                else:
                    if(user.isEnded == True):
                        #isAsked_T = True
                        message = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"
                        #line_bot_api.reply_message(event.reply_token,message)
    #---------------------發音處理訊息------------------
        elif(user.function_status == 'speech'):
            myId = event.source.user_id
            print('start_s:', user.start_s)
            if(user.start_s == 1):
                message = TextSendMessage(text="歡迎來到發音練習！\n\n在發音練習裡，你可以選擇練習不同難易度的發音，一組題目會有10題！\n\n題目分成詞彙與句子兩種類型，越早答對就可以獲得更多星星哦！\n\n第一次就答對：🌟🌟\n第二次才答對：🌟\n第三次才答對：❌")
                line_bot_api.push_message(myId, message)
                setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/zaHN8Q.jpg','發音練習','唸不出正確的發音嗎?')
                line_bot_api.reply_message(event.reply_token, setlevel_bubble)
#----------------積分處理訊息------------------
        elif(user.function_status == 'score'):
            reset_s(user)
            score_bubble = total_score(user)
            message = FlexSendMessage(alt_text="score_bubble", contents = score_bubble)
            line_bot_api.reply_message(event.reply_token, message)
    #-----------闖關處理訊息--------------------
        elif(user.function_status =='game'):
            if(user.isInit_P == True):
                user.isInit_P = False
                smallpuzzle(event,'d00000',sheet_d0, user)       
            if user.next_id == 'd00002':
                print("detect user name")
                if event.message.type == 'text':
                    user.name = event.message.text
                    print(event.message.text)
                    print(user.name)
                smallpuzzle(event, user.next_id , user.levelsheet_d, user)
        #TODO END-------------------------------------

#------------語音處理訊息----------------
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    user = getUser(event.source.user_id)
    if(user.function_status == 'speech' or user.function_status == 'game'):
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

        # except sr.UnknownValueError:
        #     if(user.count_S != 1):
        #         wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain','')
        #         message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
        #         line_bot_api.reply_message(event.reply_token,message)
        #         user.count_S -= 1
        #     elif(user.count_S == 1):
        #             if(user.index_S == 9):
        #                 loseBubble = finalBubble('再接再厲!!', '好可惜哦!\n往上滑再聽一次正確發音吧!', user.stt_mes)
        #             else:
        #                 loseBubble = loseBubble = nextBubble('好可惜哦!\n往上滑再聽一次正確發音吧!','再接再厲!!',user.stt_mes)
        #             message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
        #             line_bot_api.reply_message(event.reply_token,message)
        #             user.count_S = 2
        #             user.index_S += 1
        except sr.RequestError as e:
            #TODO   -------------------------------------
            if user.isPuzzle_P == True:
                checkAnswer('1', '2', user, event)
                
            else:
                print("user.isPuzzle_P = False!!")
        #TODO END-------------------------------------
            if(user.count_S != 1):
                wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain','')
                message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                line_bot_api.reply_message(event.reply_token,message)
                user.count_S -= 1
            elif(user.count_S == 1):
                    if(user.index_S == 9):
                        loseBubble = finalBubble('再接再厲!!', '好可惜哦!\n往上滑再聽一次正確發音吧!', user.stt_mes)
                    else:
                        loseBubble = loseBubble = nextBubble('好可惜哦!\n往上滑再聽一次正確發音吧!','再接再厲!!',user.stt_mes)
                    message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.count_S = 2
                    user.index_S += 1            
        except Exception as e:
            #TODO -------------------------------------
            if user.isPuzzle_P == True:
                checkAnswer('1', '2', user, event)

            else:
                print("user.isPuzzle_P = False!!")
#TODO END-------------------------------------
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
        print('忽略符號語音訊息：', output_mes)
#TODO -------------------------------------
        if user.isPuzzle_P == False:
            print("user.isPuzzle_P = False!!")
            output_ans = '@@@'
#TODO 移來這裡～ 判斷Fuction是Speech再做 
            user.QA_[user.index_S][1] = user.QA_[user.index_S][1].lower()
            output_ans = ''.join(se for se in user.QA_[user.index_S][1] if se not in exclude)
#TODO END-------------------------------------  
            print('忽略符號解答：', output_ans)
            print('語音處理 QA_[index_S][1]', user.QA_[user.index_S][1])
            #message = TextSendMessage(text="辨識結果：" + output_mes)
            #line_bot_api.push_message(myId, message)
            if(user.index_S < user.qNum_S): #做完本輪題庫數目
                if(output_mes != output_ans):
                    if(user.count_S != 1):
                        wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain', user.stt_mes)
                        message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        user.count_S -= 1
                    elif(user.count_S == 1):
                        if(user.index_S == 9):
                            loseBubble = finalBubble('再接再厲!!', '好可惜哦!\n往上滑再聽一次正確發音吧!', user.stt_mes)
                        else:
                            loseBubble = loseBubble = nextBubble('好可惜哦!\n往上滑再聽一次正確發音吧!','再接再厲!!',user.stt_mes)
                        message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        user.count_S = 2
                        user.index_S += 1
                else:
                    user.star_num_s += user.count_S
                    if(user.count_S == 2):
                    reply = '你好棒!一次就答對了!'
                    elif(user.count_S == 1):
                        reply = '好棒哦!你答對了!'
                    print(user.count_S, reply)
                    if(user.index_S == 9):
                        reply = '好棒哦!你答對了!'
                        correctBubble = finalBubble('恭喜答對!!', reply, user.stt_mes)
                        user_sheet.update_cell(user.index, 8, 1)
                    else:
                        correctBubble = rightBubble(reply)
                    message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.index_S += 1
                    user.count_S = 2
#TODO -------------------------------------       
        else: #puzzle 功能語音結果比對   
            if user.test_type_list[user.index_P] == 3:
                user.sheet_word_s[user.index_P][1] = user.sheet_word_s[user.index_P][1].lower()
                output_ans = ''.join(se for se in user.sheet_word_s[user.index_P][1] if se not in exclude)
                print('語音處理 sheet_word_s[index_P][1]', user.sheet_word_s[user.index_P][1])

            elif user.test_type_list[user.index_P] == 4:
                user.sheet_sen_s[user.index_P][1] = user.sheet_sen_s[user.index_P][1].lower() 
                output_ans = ''.join(se for se in user.sheet_sen_s[user.index_P][1] if se not in exclude)
                print('語音處理 sheet_sen_s[index_P][1]', user.sheet_sen_s[user.index_P][1])
            print("!!---speech checkAnswer---!!")
            checkAnswer(output_mes, output_ans, user, event)
#TODO END------------------------------------- 
#-----------------語音處理訊息結束----------------

#出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    #print('event.postback.data:', event.postback.data)
    user = getUser(event.source.user_id)
    if(user.function_status == 'quiz'):
        #print("---Feedback QA---")
        print("---postbackData QA= ",event.postback.data )
        if(user.isChangingLevel_Q==True):
            level_bubble = setLevel_Q(event.postback.data,user) 
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 

        elif(event.postback.data == "start"):  #第七題開始需要先主動送文章再出題
            if(user.index_Q == 7 and user.count_Q == 2):
                user.sheet_Q = user.data_Reading
                user.subindex_Q = random.randrange(1, len(np.transpose([user.sheet_Q])[0]), 3)
                QA_bubble_article = QA_Bubble.Article(user.sheet_Q,user.subindex_Q)
                article = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble_article)
                line_bot_api.push_message(event.source.user_id, article)
            user.isStart_Q = True

        elif(user.isStart_Q == True):
            print("---QA correctAns scan---")
            if user.isVoc == True:
                correctAns = str(user.VocQA[user.index_Q][2])
            else:
                correctAns = str(user.sheet_Q[user.subindex_Q][4])
            print("correct answer = ",correctAns)
            print("answer index_Q = ", user.index_Q)
            print("answer subindex_Q = ", user.subindex_Q)

            if(user.index_Q < user.qNum_Q): #做完本輪題庫數目
                if event.postback.data != correctAns:
                    print("QA ~~ != correctAns")
                    if(user.count_Q != 1):
                        user.isStart_Q = False
                        wrongBubble = tryagainBubble("請再想想!!", "答案不對哦~你再想想看!", 'start', ' ')
                        message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        user.count_Q -= 1
                    elif(user.count_Q == 1):
                        user.isStart_Q = False
                        if(user.index_Q == 9):
                            loseBubble = finalBubble('再接再厲！!', '好可惜哦~答案是('+ correctAns +')才對哦!', ' ')
                        else:    
                            loseBubble = nextBubble('好可惜哦~答案是('+ correctAns +')才對哦!','再接再厲', ' ')
                        message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        user.count_Q = 2
                        user.index_Q += 1
                    user.isAsked_Q = False
                else:
                    user.isStart_Q = False
                    user.star_num_Q += user.count_Q
                    if(user.count_Q == 2):
                        reply = '你好棒!一次就答對了!'
                    elif(user.count_Q == 1):
                        reply = '好棒哦!你答對了!'
                    #print(user.count_Q, reply)
                    if(user.index_Q == 9):
                        print("last Q")
                        reply = '好棒哦!你答對了!'
                        correctBubble = finalBubble('恭喜答對!!', '好棒哦!你答對了!', ' ')
 
                    else:
                        correctBubble = rightBubble(reply)
                    message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.index_Q += 1
                    user.count_Q = 2
                    if(user.index_Q < 10):
                        user.isAsked_Q = False
                print('after count_Q: ', user.count_Q)
                print('after index_Q: ', user.index_Q)
        
        elif(event.postback.data == "end"):
            user.score = int(user_data[user.data_row][2])
            user.qa_score = int(user_data[user.data_row][3])
            user_sheet.update_cell(user.index, 3, user.score + user.star_num_Q)
            user_sheet.update_cell(user.index, 4, user.qa_score + user.star_num_Q)
            starBubble = totalStarBubble(user, user.star_num_Q)
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
            user.isStart_Q = False

        elif (event.postback.data == "next"): 
            user.index_Q = 0
            user.star_num_Q = 0
            print("答題分數顯示完 圖數和分數歸零----",user.index_Q,user.star_num_Q)
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)  

        elif (event.postback.data == "changeLevel"): 
            user.isChangingLevel_Q = True
            user.isOthertext = False

        elif (event.postback.data == "next2"):
            user.isStart_Q = True
            user.isAsked_Q = True
            user.data_Voc, user.data_Reading, user.data_Cloze = getSheetQA(user.level_Q) #預設傳level = 1
            user.sheet_Q = getVoc.editSheet(user.data_Voc)
            QA_bubble = Question_Q(user)
            message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
            line_bot_api.reply_message(event.reply_token, message)
        elif (event.postback.data == "AllEnd"):
            message = TextSendMessage(text="謝謝你使用解題小達人～～\n歡迎點開下方選單，使用其他功能使用其他功能哦！")
            line_bot_api.reply_message(event.reply_token, message)
#------------------聽力回饋判斷-------------------
    elif(user.function_status == 'listen'):
        print("---Feedback---")
        user = getUser(event.source.user_id)
        if(user.isChangingLevel_L==True):
            level_bubble = setLevel(event.postback.data,user) 
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
            setUserCountType(user)
            user.count_L = user.count_type_L

        elif(event.postback.data == "start"):  
            user.isStart_L = True

        elif(user.isStart_L == True): 
            if user.isWord == True:
                correctAns = str(user.word_list[user.subindex_L][2])

            else:
                correctAns = str(user.sheet_L[user.subindex_L][4])
            print("correct answer = ",correctAns)
            print("answer user.index_L = ", user.index_L)
            print("answer subuser.index_L = ", user.subindex_L)
            if(user.index_L < user.qNum_L): #做完本輪題庫數目
                if event.postback.data != correctAns:
                    if(user.count_L != user.count_type_L - 1):
                        user.isStart_L = False
                        wrongBubble = tryagainBubble("請再想想!!", "答案不對哦~你再想想看!", 'start', ' ')
                        message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        user.count_L -= 1
                    elif(user.count_L == user.count_type_L - 1):
                        user.isStart_L = False
                        if(user.index_L == 9):
                            loseBubble = finalBubble('再接再厲！!', '好可惜哦~答案是('+ correctAns +')才對哦!', ' ')
                        else:    
                            loseBubble = nextBubble('好可惜哦~答案是('+ correctAns +')才對哦!','再接再厲', ' ')
                        message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        setUserCountType(user)
                        user.count_L = user.count_type_L
                        user.index_L += 1
                    user.isAsked_L = False
                else:
                    user.isStart_L = False
                    user.star_num_L += user.count_L
                    if(user.count_L == user.count_type_L):
                        reply = '你好棒!一次就答對了!'
                    elif(user.count_L == user.count_type_L - 1):
                        reply = '好棒哦!你答對了!'
                    if(user.index_L == 9):
                        reply = '好棒哦!你答對了!'
                        correctBubble = finalBubble('恭喜答對!!','好棒哦!你答對了!', ' ')
                    else:
                        correctBubble = rightBubble(reply)
                    message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    user.index_L += 1
                    if(user.index_L < 10):
                        user.isAsked_L = False
                    setUserCountType(user)
                    user.count_L = user.count_type_L
                print('after user.count_L: ', user.count_L)
                print('after user.index_L: ', user.index_L)
        
        elif(event.postback.data == "end"):
            user.score = int(user_data[user.data_row][2])
            user.lis_score = int(user_data[user.data_row][4])
            user_sheet.update_cell(user.index, 3, user.score + user.star_num_L)
            user_sheet.update_cell(user.index, 5, user.lis_score + user.star_num_L)
            starBubble = totalStarBubble(user, user.star_num_L)
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
            user.isStart_L = False

        elif (event.postback.data == "next"): 
            user.index_L = 0
            user.star_num_L = 0
            user.word_list = []
            print("答題分數顯示完 圖數和分數歸零----",user.index_L,user.star_num_L)
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)  

        elif (event.postback.data == "changeLevel"): 
            user.isChangingLevel_L = True
            user.isOthertext = False

        elif (event.postback.data == "next2"):#直接繼續答題 不換程度
            user.isStart_L = True
            user.isAsked_L = True
            QA_bubble = Question(user)
            message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
            line_bot_api.reply_message(event.reply_token, message)
        elif (event.postback.data == "AllEnd"):
            message = TextSendMessage(text="謝謝你使用聽力練習～～\n歡迎點開下方選單，使用其他功能使用其他功能哦！")
            line_bot_api.reply_message(event.reply_token, message)
#-----------------翻譯回饋判斷-------------------
    elif(user.function_status == 'translation'):
        user = getUser(event.source.user_id)
        print("---Feedback---")
        user.levelinput = event.postback.data
        if(user.isChangingTrans==True):
            user.isChangingTrans = False
            if (user.levelinput=='ETC'):
                user.TransType = 1
                print("切換英翻中模式,請您傳送只有英文的單字或句子～")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "切換英翻中模式,\n請您傳送只有英文的單字或句子～"))
                user.isAsked_T = False

            elif (user.levelinput=='CTE'):
                user.TransType = 2
                print("切換中翻英模式,請您傳送只有中文的單字或句子～")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "切換中翻英模式,\n請您傳送只有中文的單字或句子～"))
                user.isAsked_T = False   
            else:       
                user.isChangingTrans = True
                user.isAsked_T = True
            
        if(user.levelinput == 'Next'):
            if(user.isEnded == False):
                if(user.TransType == 1):
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請將你想翻譯的詞彙或句子傳送給我~"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請將你想翻譯的詞彙或句子傳送給我~"))
        
                user.isAsked_T = False
        
        if(user.levelinput == 'End'):
            user.isEnded = True
            user.isAsked_T = True  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"))
#-----------------語音回饋判斷----------------------------------------
    elif(user.function_status == 'speech'):
        print("---Feedback---")
        user = getUser(event.source.user_id)
        if(event.postback.data == 'L' or event.postback.data == 'M' or event.postback.data == 'H'):
            user.level = event.postback.data
            level_bubble = setLevel_S(event.postback.data, user)
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
        elif(event.postback.data == "start"):
            speech_bubble = QA_S(user.QA_[user.index_S][0], user.QA_[user.index_S][1], user, user.index_S)
            message = FlexSendMessage(alt_text="speech_bubble", contents = speech_bubble)
            line_bot_api.reply_message(event.reply_token, message)
        elif(event.postback.data == "end"):
            user.score = int(user_data[user.data_row][2])
            user.speech_score = int(user_data[user.data_row][5])
            user_sheet.update_cell(user.index, 3, user.score + user.star_num_s)
            user_sheet.update_cell(user.index, 6, user.speech_score + user.star_num_s)
            starBubble = totalStarBubble(user, user.star_num_s)
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
        elif (event.postback.data == "next"):
            user.index_S = 0
            user.star_num_s = 0
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)

        elif (event.postback.data == "changeLevel"):
            user.isChangingLevel_L = True
        elif (event.postback.data == "next2"):
            level_bubble = setLevel_S(user.level, user)
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
        elif(event.postback.data == "tryagain"):
            message = TextSendMessage(text="請再透過語音訊息唸給我聽一次～")
            line_bot_api.reply_message(event.reply_token, message)
        elif (event.postback.data == "AllEnd"):
            message = TextSendMessage(text="謝謝你使用發音練習～～\n歡迎點開下方選單，使用其他功能使用其他功能哦！")
            line_bot_api.reply_message(event.reply_token, message)
    #TODO -------------------------------------
#--------------闖關回饋訊息----------------------
    elif(user.function_status == 'game'):
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
            if pb_event == 'f1':
                #了解背景故事
                smallpuzzle(event,'d00100',sheet_d0, user)

            elif pb_event == 'f2':
                #開始遊戲
                smallpuzzle(event,'d00200',sheet_d0, user)

            elif pb_event == 'f3':
                #結束遊戲
                user.score = int(user_data[user.data_row][2])
                user.game_score = int(user_data[user.data_row][6])
                user_sheet.update_cell(user.index, 3, user.score + user.star_num_P)
                user_sheet.update_cell(user.index, 7, user.game_score + user.star_num_P)
                reset_P(user)
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
#TODO END-------------------------------------

def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar(user_ID)
        allUser.append(user)
        #print("Alluser",allUser)
    return user
    
##出題小老師  出題類型ＵＩ------------------------------------------------
def typeButtonQA():
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

def setLevel_Q(levelinput, user):
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
        user.isOthertext = False
        myResult = "N"

    if user.isChangingLevel_Q == False:
        user.data_Voc, user.data_Reading, user.data_Cloze = getSheetQA(user.level_Q)
        #sheet_Q = editSheet(pre_sheet)
        #print("更換難易度後 更新取得新的隨機題目----level_Q get sheet_Q",sheet_Q)
      
    return myResult

def Question_Q(user):
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
        #user.subindex_Q = user.index_Q - 3 
        user.sheet_Q = user.data_Cloze
        print("data_Cloze len",len(np.transpose([user.sheet_Q])[0]))
        if user.count_Q == 2:
            user.subindex_Q = random.randrange(1,len(np.transpose([user.sheet_Q])[0]))
            print("data_Cloze subindex_Q", user.subindex_Q)
        if (user.level_Q != 3):
            QA_bubble = QA_Bubble.Cloze(user.sheet_Q, user.index_Q, user.subindex_Q)
        else:
            QA_bubble = QA_Bubble.Cloze_L3(user.sheet_Q, user.index_Q, user.subindex_Q)

    else:
        #user.subindex_Q = user.index_Q - 7
        if (user.index_Q != 7 and user.count_Q == 2):
            user.subindex_Q = user.subindex_Q + 1
        
        print("user.subindex_Q",user.subindex_Q)
        QA_bubble = QA_Bubble.Reading(user.sheet_Q,user.index_Q,user.subindex_Q)
        
    return QA_bubble
#----------聽力function------------------
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
        user.isOthertext = False
        myResult = "N"

    if user.isChangingLevel_L == False:
        user.data_pho, user.data_word, user.data_sen = getSheet(user.level_L)

    return myResult

def setUserCountType(user):
    if user.index_L < 3 and user.level_L !=3:
        user.count_type_L = 1
    else:
        user.count_type_L = 2

def Question(user):
    # global user.subindex_L,user.sheet_L
    print("選完階級！開始出題")
    if user.index_L < 3:
        if user.level_L != 3:
            if user.count_L == user.count_type_L :
                user.sheet_L = user.data_pho
                user.subindex_L = random.randrange(1,len(np.transpose([user.sheet_L])[0]))
            print(user.sheet_L)
            QA_bubble = QA.QA_Tail(user.sheet_L,user.index_L,user.subindex_L)
        else: #高級前三題，題目不同
            print("*****change ～～")
            if user.count_L == user.count_type_L :
                user.sheet_L = user.data_pho
                user.subindex_L = random.randrange(1,len(np.transpose([user.sheet_L])[0]))
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
            print("user.word_list",user.word_list[user.subindex_L])
            print("user.word_list[2]",user.subindex_L, user.word_list[user.subindex_L][2])
            QA_bubble = QA.QA_Word(user.index_L, user.word_list[user.subindex_L])
    else:
        user.isWord = False
        if user.count_L == user.count_type_L :
            user.sheet_L = user.data_sen
            user.subindex_L = random.randrange(1,len(np.transpose([user.sheet_L])[0])) 
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
                        thumbnail_image_url = pic_url,
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

def totalStarBubble(user,star_num):
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
                    action = PostbackAction(label = "我不答了", data = 'AllEnd', text = "我不答了"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble

def total_score(user):
    user.score = int(user_data[user.data_row][2])
    user.qa_score = int(user_data[user.data_row][3])
    user.lis_score = int(user_data[user.data_row][4])
    user.speech_score = int(user_data[user.data_row][5])
    user.game_score = int(user_data[user.data_row][6])
    Bubble = BubbleContainer (
        direction='ltr',
        hero= ImageComponent(
            url="https://dlms.iiiedu.org.tw/eng/img/stars.png", size='full', aspect_ratio="20:13", aspect_mode="cover"
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="星星總數", size='xl', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="你的星星總數：",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(user.score) + "顆",flex = 0, margin = 'md', size='lg', color = '#F10000')
                        ]
                ),
                TextComponent(text="解題小達人", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="你獲得的星星：",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(user.qa_score) + "顆",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="聽力練習", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="你獲得的星星：",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(user.lis_score) + "顆",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="發音練習", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="你獲得的星星：",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(user.speech_score) + "顆",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="闖關遊戲", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="你獲得的星星：",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(user.game_score) + "顆",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                )
            ]  
        ),
        footer = BoxComponent(
            layout='vertical', flex = 0, spacing = 'sm',
            contents=[
                SpacerComponent(size = 'sm')
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
##  End------------------------------------------------

#-----------------翻譯function--------------------------
def translation(text, user):
    translator = Translator()
    #lang = translator.detect(event.message.text)
    #print("Lang=",lang.lang)
    if user.TransType == 2: 
        #if lang.lang == "zh-CN" :
        print("---- transmeaasge C to E -----")
        translateMessage = translator.translate(text, dest='en')
        print("trans =",translateMessage.text)
        #message = TextSendMessage(text=translateMessage.text)
    elif user.TransType == 1:
        #lang.lang =="en":
        print("---- transmeaasge E to C -----")
        translateMessage = translator.translate(text, dest='zh-tw')
        print("trans =",translateMessage.text)
        #message = TextSendMessage(text=translateMessage.text)

    #print("message=",translateMessage) 
    return translateMessage.text   

def Choose_NextStep():
    Translation_bubble = BubbleContainer (
                    body = BoxComponent(
                        layout='vertical',
                        contents=[
                            ButtonComponent(
                                action = PostbackAction(label = '翻下一句', data = 'Next', text = None),
                                color = '#F1C175',
                                style = 'primary',
                                gravity = 'center',
                                margin = 'md'
                            ),
                            ButtonComponent(
                                action = PostbackAction(label = '結束翻譯', data = 'End', text = None),
                                color = '#E18876',
                                margin = 'md',           
                                style = 'primary',
                                gravity = 'center'
                            )
                        ]
                    )
                )   
    return Translation_bubble

#-----------------發音Function------------
#TODO 原本直接用的user.index_S 改用傳入index。 
# PS.阿書這邊原本有call此Func 的也再記得改一下傳入index囉！！^^ 感謝！------------------------------------- 
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
#TODO END-------------------------------------

def setLevel_S(levelinput, user):
    user.L1_qa = random.sample(L1_voc_data, 5)
    user.L1_qa.extend(random.sample(L1_sen_data, 5))
    user.L2_qa = random.sample(L2_voc_data, 5)
    user.L2_qa.extend(random.sample(L2_sen_data, 5))
    user.L3_qa = random.sample(L3_voc_data, 5)
    user.L3_qa.extend(random.sample(L3_sen_data, 5))
    print("---Changing Level---")
    if (levelinput=='L'):
        user.QA_ = user.L1_qa
        myResult = readyBubble(1)
        
    elif (levelinput=='M'):
        user.QA_ = user.L2_qa
        myResult = readyBubble(2)

    elif (levelinput=='H'):
        user.QA_ = user.L3_qa
        myResult = readyBubble(3)

    else:
        myResult = "N"

    if user.isChangingLevel_L == False:
        print("選擇好的難易題目： ", user.QA_)
    user.start_s = 0 
    return myResult
#----------------end----------------
#-------------答題判斷function-------------
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

def tryagainBubble(str1, str2, str3, meg_s):
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = str1, weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = str2, size='xs', align = 'center', gravity = 'top'),
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top', wrap = True)
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

def nextBubble(feedback, str, meg_s):
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
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top', wrap = True)
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '跳下一題', data = 'start', text = '跳下一題'),
                    color = '#45E16E',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble

def finalBubble(str1, str2, meg_s):
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
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top', wrap = True)
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

#TODO -------------------------------------
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

    user.data_pho, user.data_word, user.data_sen = getSheet(user.level_P)
    user.data_Voc, user.data_Reading, user.data_Cloze = getSheetQA(user.level_P) #預設傳level = 1
    getSheet_S(user.level_P, user)

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
            print("level = ",user.level_P)
            setLevelStory(event, user)
            #user.isGetSheet_P = True
        
        #---------------------------------------------------

        #剛開始答題
        elif id == 'd10030' or id == 'd20025' or id == 'd30022':
            RandomTest(user)
            user.isLoad_P = True
        elif (int(id[1:2]) == (user.level_P)):#非d0表單
            if(int(id[2:3]) == (user.test_type_list[user.index_P])):  
                #答對
                if id[3:4] == '1': 
                    if  user.index_P < 9:
                        print("答對 繼續isLoad_P")
                        user.index_P += 1
                        user.isLoad_P = True
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
                #第一次答錯
                elif id[3:4] == '2':
                    if user.index_P < 9:
                        print("第一次答錯 再一次 isStart_P，Load題目")
                        user.isStart_P = True
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
                #第二次答錯
                elif id[3:4] == '3':
                    if user.index_P < 9:
                        user.index_P += 1
                        user.isLoad_P = True
                        print("第二次答錯 新題目PreStory")
                    else:
                        smallpuzzle(event,'d'+ str(user.level_P) + '0100', user.levelsheet_d, user)
            #---------------------------------------------------  
            #----計算最後答題結果
            #是否大於六題
            elif id[2:4] == '01':
                if user.star_num_P >= 2:
                    smallpuzzle(event,'d'+ str(user.level_P) + '0200', user.levelsheet_d, user)
                else:
                    smallpuzzle(event,'d'+ str(user.level_P) + '0300', user.levelsheet_d, user)
            #結尾故事
            elif id[2:4] == '02' or id[2:4] == '03':
                smallpuzzle(event,'d'+ str(user.level_P) + '0400', user.levelsheet_d, user)

            #結束 回到最初功能選擇
            elif id[2:4] == '04':
                user.score = int(user_data[user.data_row][2])
                user.game_score = int(user_data[user.data_row][6])
                user_sheet.update_cell(user.index, 3, user.score + user.star_num_P)
                user_sheet.update_cell(user.index, 7, user.game_score + user.star_num_P)
                reset_P(user)
                smallpuzzle(event,'d00003',sheet_d0, user)

            if user.isPreStory_P == True:
                print("PreStory End! Strat Testing!")
                user.isStart_P = True
                user.isAsked_P = False
                user.isPreStory_P = False
        
        pass
#def SpecialCaseDetect():
    
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
    user.test_type_list = [random.randint(1,7) for _ in range(10)]
    print("-----*** Quiz type = ",user.test_type_list)

def LoadTestIndex(user):
    print("-----LoadTestIndex----", user.index_P)
    #題數引文
    if user.level_P == 1 :
        test_pretext = "（第" + str(user.index_P+1) + " 題）\n【Silas】：\n勇者$username ，現在是 "+ str(8+user.index_P) +":00，Ariel 希望我們在傍晚18:00前完成。"
        print(test_pretext)
        message = TextBubble(test_pretext)
    
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
        test_type1 = random.randint(1, 2)
        if test_type1 == 1:
            print("--sheet_pho--")
            if user.level_P != 3:
                user.count_type_P = 1
                
                if user.count_P == 2:
                    user.count_P = 1
                
                if user.count_P == user.count_type_P:
                    print("random QA_Tail subindex")
                    user.text_sheet_P = user.data_pho
                    user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0]))
                user.text_sheet_P = user.data_pho
                bubble = QA.QA_Tail(user.text_sheet_P,user.index_P,user.subindex_P)
            else: #高級前三題，題目不同
                print("---level 3 pho  依據音檔選句子---")
                if user.count_P == user.count_type_P :
                    user.text_sheet_P = user.data_pho
                    user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0]))
                bubble = QA.QA_Sentence(user.text_sheet_P,user.index_P,user.subindex_P,'依據音檔，選出最適當的答案')
        else:
            print("--sheet_word--",test_type1)
            user.isWord = True
            if user.count_P == user.count_type_P:
                user.text_sheet_P = getVoc.editSheet(user.data_word)
                q_index, q_chinese, q_english = getVoc.getVoc(user.text_sheet_P)
                option_english,option_english2 = getVoc.getOption(user.text_sheet_P, q_index)
                option, answer = getVoc.getQA(q_english, option_english,option_english2)
                q_audio = getVoc.getAudio(user.text_sheet_P, q_index)
                user.word_list = [q_audio, option, answer]
            print("user.word_list",user.word_list)
            bubble = QA.QA_Word(user.index_P, user.word_list)
    
    elif user.test_type_list[user.index_P] == 2:
        print("sheet_L_sen")
        user.text_sheet_P = user.data_sen
        if user.count_P == user.count_type_P :
            print("random subindex_P")
            user.subindex_P = random.randrange(1,len(np.transpose([user.text_sheet_P])[0])) 
        print("user.subindex_P",user.subindex_P)
        bubble = QA.QA_Sentence(user.text_sheet_P,user.index_P,user.subindex_P,'選出正確的應對句子')
    
    elif user.test_type_list[user.index_P] == 3:
        print("sheet_speaking_word")
        bubble = QA_S(user.sheet_word_s[user.index_P][0], user.sheet_word_s[user.index_P][1], user, user.index_P)

    elif user.test_type_list[user.index_P] == 4:
        print("sheet_speaking_sen")
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
        if(user.count_P == user.count_type_P):
            user.text_sheet_P = user.data_Reading
            print("reading", len( np.transpose( [user.text_sheet_P])[0] ) )
            user.subindex_P = random.randrange(1, len(np.transpose([user.text_sheet_P])[0]), 3)
            QA_bubble_article = QA_Bubble.Article( user.text_sheet_P, user.subindex_P )
            article = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble_article)
            line_bot_api.push_message(event.source.user_id, article)
        
        bubble = QA_Bubble.Reading(user.data_Reading, user.index_P, user.subindex_P)
                                                                                                                                                                         
    return bubble
#TODO END-------------------------------------

#TODO ------------------------------------- 
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
#TODO END------------------------------------- 

def reset_s(user):
    user.start_s = 1
    user.star_num_s = 0
    user.index_S = 0
    user.count_S = 2
    user.qNum_S = 10
    user.score = 0
    user.L1_qa = []
    user.L2_qa = []
    user.L3_qa = []
    user.speech = False
    user.stt_mes = ''
    user.QA_.clear()

def reset(user):
    user.isAsked_Q = False #出題與否
    user.isChangingLevel_Q = True
    user.isStart_Q = False
    user.index_Q = 0 #第幾題
    user.isInit_Q = True
    user.subindex_Q = user.index_Q
    user.star_num_Q = 0
    user.count_Q = 2
    user.isVoc = False 
    user.VocQA = []
    user.isAsked_L = False #出題與否
    user.isChangingLevel_L = True
    user.isStart_L = False
    user.index_L = 0 #第幾題
    user.isInit_L = True
    user.subindex_L = user.index_L
    user.count_L = 2
    user.star_num_L = 0
    user.isWord = False
    user.word_list = []
    user.isInit_T = True
    user.isAsked_T = True
    user.isChangingTrans = True
    user.isEnded = False
    user.TransType = 1
    user.score = 0
    user.isOthertext = False

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
