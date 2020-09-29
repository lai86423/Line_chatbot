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

app = Flask(__name__)

#書
line_bot_api = LineBotApi('Ay6xk+FmKxu4tFPtdzXBMR/V8Mf1GnwNi07Vt9QgOHCHwUCd3x8pdRMu7rTHR1/QWlcVcaaHRzfi9gARYXgNqm7WT7M7YoeWJv+NFkl+iZg5K0jAERYZud6HpNmpVXm6TEIf7ZY1DxnH55E77umPawdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('533dbc0dab0d92eea7a87b05cb7e49a6')

# #映
# line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')

# handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#-------功能變數--------
trans = False
quiz = False
listen = False
stt = False
grade = False
#------------------
#-------抓user_id------
user_data = []
user_index = 0
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
        #
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
        #Trans
        self.isAsked_T = True
        self.isChangingTrans = True
        self.isEnded = False
        self.TransType = 1
        self.isInit_L = True

##-----------------------------------------------------------------------------------
##聽力  初始抓資料＆資料處理
# GDriveJSON = 'JSON.json'
# GSpreadSheet_L = 'cilab_ChatBot_listening'
# gc_L = pygsheets.authorize(service_account_file='JSON.json') #檔案裡的google user.sheet_L js檔
# sh_L = gc_L.open(GSpreadSheet_L)
# sh_L.worksheet_by_title('L1_pho').export(filename='L1_pho')
# sh_L.worksheet_by_title('L1_sen').export(filename='L1_sen')
# sh_L.worksheet_by_title('L2_pho').export(filename='L2_pho')
# sh_L.worksheet_by_title('L2_sen').export(filename='L2_sen')
# sh_L.worksheet_by_title('L3_pho').export(filename='L3_pho')
# sh_L.worksheet_by_title('L3_sen').export(filename='L3_sen')

# #type: <class 'pandas.core.frame.DataFrame'>
# L1_pho = pd.read_csv('L1_pho.csv')
# L1_sen = pd.read_csv('L1_sen.csv')
# L2_pho = pd.read_csv('L2_pho.csv')
# L2_sen = pd.read_csv('L2_sen.csv')
# L3_pho = pd.read_csv('L3_pho.csv') 
# L3_sen = pd.read_csv('L3_sen.csv')

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

# def editSheet(data):
#     pre_sheet = data.sample(frac =0.1) #Random打亂資料再取n筆題 
#     pre_sheet = pre_sheet.reset_index(drop=True)
#     print("pre_sheet",pre_sheet)
#     header = pre_sheet.columns
#     sheet_L = {}
#     for i in range (len(header)):
#         sheet_L[header[i]] = pre_sheet[header[i]]
    
#     #qNum_L = len(sheet["question"])
#     return sheet_L
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
L1_sen_sheet = spreadSheet.worksheet("L1_sen")
L1_sen_data = L1_sen_sheet.get_all_values()
del(L1_sen_data[0])
L2_voc_sheet = spreadSheet.worksheet("L2_voc")
L2_voc_data = L2_voc_sheet.get_all_values()
del(L2_voc_data[0])
L2_sen_sheet = spreadSheet.worksheet("L2_sen")
L2_sen_data = L2_sen_sheet.get_all_values()
del(L2_sen_data[0])
L3_voc_sheet = spreadSheet.worksheet("L3_voc")
L3_voc_data = L3_voc_sheet.get_all_values()
del(L3_voc_data[0])
L3_sen_sheet = spreadSheet.worksheet("L3_sen")
L3_sen_data = L3_sen_sheet.get_all_values()
del(L3_sen_data[0])
#-------------------查看積分變數-------------------
check_grade = True
choose = '0'

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
    global trans, quiz, listen, stt, grade, speech
    global user_index, data_row
    global user_data
    global score, qa_score, lis_score, trans_score, speech_score, game_score, function_status
    global check, check_user, strat_S
    global user_sheet
    user = getUser(event.source.user_id)
    user_data = user_sheet.get_all_values()
    #print('!!!!!!!!!!!!!!!!!!user:', user_data)
    for i in range(1,len(user_data)):
        #print('user_data[i][0]:',user_data[i][0])
        #print('id:', event.source.user_id)
        #print('user_data[i][0]:',user_data[i][1])
        if (user_data[i][0] == event.source.user_id):
            check_user = True
            user_index = i + 1
            #print('find user!!!!')
            break
    #print('check_user: ', check_user)
    if (check_user == False):
        user_index = len(user_data) + 1
        user_sheet.add_rows(1)
        user_sheet.update_cell(user_index, 1, event.source.user_id)
        user_sheet.update_cell(user_index, 2, 'null')
        user_sheet.update_cell(user_index, 3, '0')
        user_sheet.update_cell(user_index, 4, '0')
        user_sheet.update_cell(user_index, 5, '0')
        user_sheet.update_cell(user_index, 6, '0')
        user_sheet.update_cell(user_index, 7, '0')
        user_data.append([event.source.user_id, 'null', 0, 0, 0, 0, 0,])
    #print('user_update:',user_data)
    #print('user_index', user_index)
    data_row = user_index - 1
    user.function_status = user_data[data_row][1]
    user.score = int(user_data[data_row][2])
    user.qa_score = int(user_data[data_row][3])
    user.lis_score = int(user_data[data_row][4])
    user.speech_score = int(user_data[data_row][5])
    user.game_score = int(user_data[data_row][6])
    check_user = False
    # print('after check_user: ', check_user)
    # print('check:', check)
    # print('event user_id: ', event.source.user_id)
    # print('user_id:', user_data[data_row][0])
    # print('user_index', user_index)
    # print('score: ', user.score)
    # print('qa_score: ', user.qa_score)
    # print('lis_score: ', user.lis_score)
    # print('speech_score: ', user.speech_score)
    # print('game_score: ', user.game_score)
    ############################################
    if event.message.type == 'text':
        if(event.message.text == '#translation'):
            reset(user)
            user.function_status = 'translation'
            user_data[data_row][1] = 'translation'
            user_sheet.update_cell(user_index, 2, 'translation')
            print('translation trans True')
        elif(event.message.text == '#quiz'):
            reset(user)
            user.function_status = 'quiz'
            user_data[data_row][1] = 'quiz'
            user_sheet.update_cell(user_index, 2, 'quiz')
            print('quiz trans True')
        elif(event.message.text == '#listen'):
            reset(user)
            user.function_status = 'listen'
            user_data[data_row][1] = 'listen'
            user_sheet.update_cell(user_index, 2, 'listen')
            print('listen trans True')
        elif(event.message.text == '#speech'):
            user.function_status = 'speech'
            reset(user)
            reset_s(user)
            user_data[data_row][1] = 'speech'
            user_sheet.update_cell(user_index, 2, 'speech')
            print('stt trans True')
        elif(event.message.text == '#score'):
            reset(user)
            user.function_status = 'score'
            user_data[data_row][1] = 'score'
            user_sheet.update_cell(user_index, 2, 'score')
            print('grade trans True')
        user.function_status = user_data[data_row][1]
        print('!!!!!-------status--------!!!!!: ', user.function_status)
    #-----------出題處理訊息-----------------
        if(user.function_status == 'quiz'):
            #global isAsked_Q,isInit_Q
            #global index_Q
            #global isChangingLevel_Q
            #global sheet_Q,subindex_Q
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
                    user.isAsked_Q = False
                    setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/V5TmMA.png','解題小達人', '總是聽不懂別人在說什麼嗎?')
                    line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
                elif user.isStart_Q == True:
                    if( user.isAsked_Q == False): 
                        user.isAsked_Q = True
                        QA_bubble = Question_Q(user)
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
#--------------聽力處理訊息--------------------
        elif(user.function_status == 'listen'):
            # global isAsked_L,isInit_L
            # global index_L
            # global isChangingLevel_L
            # global sheet,subindex
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
                    user.isAsked_L = False
                    setlevel_bubble = levelBubble('https://upload.cc/i1/2020/06/08/jhziMK.png','聽力練習','總是聽不懂別人在說什麼嗎?')
                    line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
                elif user.isStart_L == True:
                    if( user.isAsked_L == False ): 
                        user.isAsked_L = True
                        QA_bubble = Question(user)
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
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
                user.L1_qa = random.sample(L1_voc_data, 5)
                user.L1_qa.extend(random.sample(L1_sen_data, 5))
                user.L2_qa = random.sample(L2_voc_data, 5)
                user.L2_qa.extend(random.sample(L2_sen_data, 5))
                user.L3_qa = random.sample(L3_voc_data, 5)
                user.L3_qa.extend(random.sample(L3_sen_data, 5))
                print('L1_qa: ', user.L1_qa)
                print('L2_a: ', user.L2_qa)
                print('L3_qa: ', user.L3_qa)
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

#------------語音處理訊息----------------
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    global trans, quiz, listen, stt, grade, speech, stt_mes, OA_
    global index_S, count_S, score, speech_score
    user = getUser(event.source.user_id)
    if(user.function_status == 'speech'):
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
        except Exception as e:
            t = '音訊有問題'+test+str(e.args)+path
            wrongBubble = tryagainBubble('請再試試!!', '還有些不正確哦~你再試試看！', 'tryagain','')
            message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
            line_bot_api.reply_message(event.reply_token,message)
        os.remove(path)
        text = r.recognize_google(audio,language='zh-CN')
        user.stt_mes = text
        print('原始語音訊息：', user.stt_mes)
        user.stt_mes = user.stt_mes.lower()
        user.QA_[user.index_S][1] = user.QA_[user.index_S][1].lower()
        print('忽略大小寫語音訊息：', user.stt_mes)
        #exclude = set(string.punctuation)
        exclude = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~' + '‘’→↓△▿⋄•！？?〞＃＄％＆』（）＊＋，－╱︰；＜＝＞＠〔╲〕 ＿ˋ｛∣｝∼、〃》「」『』【】﹝﹞【】〝〞–—『』「」…﹏'
        output_mes = ''.join(ch for ch in user.stt_mes if ch not in exclude)
        output_ans = ''.join(se for se in user.QA_[user.index_S][1] if se not in exclude)
        print('忽略符號語音訊息：', output_mes)
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
                user.score += user.count_S
                user.speech_score += user.count_S
                print('score: ', user.score)
                print('speech_score: ', user.speech_score)
                user_sheet.update_cell(user_index, 3, user.score)
                user_sheet.update_cell(user_index, 6, user.speech_score)
                print('save!!!!!!!!!!')
                print('正確答案!')
                user.count_S = 2
                if(user.count_S == 2):
                   reply = '你好棒!一次就答對了!'
                elif(user.count_S == 1):
                    reply = '好棒哦!你答對了!'
                print(user.count_S, reply)
                if(user.index_S == 9):
                    reply = '好棒哦!你答對了!'
                    correctBubble = finalBubble('恭喜答對!!', reply, user.stt_mes)
                    user_sheet.update_cell(user_index, 8, 1)
                else:
                    correctBubble = rightBubble(reply)
                message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                line_bot_api.reply_message(event.reply_token,message)
                user.index_S += 1
#-----------------語音處理訊息結束----------------

#出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    global trans, quiz, listen, stt, score, qa_score, lis_score, trans_score, speech_score, game_score, function_status
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
                    user.score += user.count_Q
                    user.qa_score += user.count_Q
                    #print('score: ', user.score)
                    #print('qa_score: ', user.qa_score)
                    user_sheet.update_cell(user_index, 3, user.score)
                    user_sheet.update_cell(user_index, 4, user.qa_score)
                    #print('save!!!!!!!!!!')
                    #print('正確答案!')
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
                    user.score += user.count_L
                    user.lis_score += user.count_L
                    #print('score : ', user.score)
                    #print('lis_score: ', user.lis_score)
                    user_sheet.update_cell(user_index, 3, user.score)
                    user_sheet.update_cell(user_index, 5, user.lis_score)
                    #print('save!!!!!!!!!!')
                    #print('正確答案!')
                    if(user.count_L == user.count_type_L):
                        reply = '你好棒!一次就答對了!'
                    elif(user.count_L == user.count_type_L - 1):
                        reply = '好棒哦!你答對了!'
                    #print(user.count_L, reply)
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
            #print('恭喜你做完這次的聽力練習了!star=',user.star_num_L)
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
                print("切換英翻中模式")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "目前切換 英文翻中文模式！\n請將你想翻譯的英文單字或句子傳送給我哦~"))
                user.isAsked_T = False

            elif (user.levelinput=='CTE'):
                user.TransType = 2
                print("切換中翻英模式")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "目前切換 中文翻英文模式！\n請將你想翻譯的中文字詞或句子傳送給我哦~"))
                user.isAsked_T = False   
            else:       
                user.isChangingTrans = True
                user.isAsked_T = True
            
        if(user.levelinput == 'Next'):
            if(user.isEnded == False):
                if(user.TransType == 1):
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請傳送英文單字或句子~"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請傳送中文字詞或句子~"))
        
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
            level_bubble = setLevel_S(event.postback.data, user)
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
        elif(event.postback.data == "start"):
            speech_bubble = QA_S(user.QA_[user.index_S][0], user.QA_[user.index_S][1], user)
            message = FlexSendMessage(alt_text="speech_bubble", contents = speech_bubble)
            line_bot_api.reply_message(event.reply_token, message)
        elif(event.postback.data == "end"):
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
            user.start_s = 1
        elif(event.postback.data == "tryagain"):
            user.speech = True
        elif (event.postback.data == "AllEnd"):
            message = TextSendMessage(text="謝謝你使用發音練習～～\n歡迎點開下方選單，使用其他功能使用其他功能哦！")
            line_bot_api.reply_message(event.reply_token, message)

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
    #global data_Voc, data_Reading, data_Cloze
    #global level_Q
    #global isChangingLevel_Q
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
def QA_S(address, ques, user):
    QA_Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="發音練習("+ str(user.index_S+1) +"/10)", weight='bold', size='lg', align = 'center')                   
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

def setLevel_S(levelinput, user):
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
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top')
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
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top')
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
                TextComponent(text = meg_s, size='xs', align = 'center', gravity = 'top')
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

def reset_s(user):
    user.start_s = 1
    user.star_num_s = 0
    user.index_S = 0
    user.count_S = 2
    user.qNum_S = 10
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
    user.isWord = False 
    user.word_list = []
    user.isInit_T = True
    user.isAsked_T = True
    user.isChangingTrans = True
    user.isEnded = False
    user.TransType = 1


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
