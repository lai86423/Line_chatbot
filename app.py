from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import sys
#import traceback
import numpy as np
import pandas as pd
from googletrans import Translator
#from openpyxl import load_workbook
#from openpyxl import Workbook
#import openpyxl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import QA
import QA_Bubble
#import datetime 
import pygsheets
#from pydub import AudioSegment
#import speech_recognition as sr
import time
#import tempfile
#from gtts import gTTS
#from pygame import mixer
#import random

app = Flask(__name__)

line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#-------�\���ܼ�--------
trans = False
quiz = False
listen = False
stt = False
grade = False
#------------------
#-------��user_id------
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
#----------------------
##ť�O  �ܼ�------------------------------------------------
level_L = 1 # �w�]level 1
qNum_L = 10 # �C���D�ؼƶq
star_num_L = 0 #���I
isAsked_L = False #�X�D�P�_
isChangingLevel_L = True
isStart_L = False
index_L = 0 #�ĴX�D
isInit_L = True
subindex_L = 0
count_L = 1
##-----------------------------------------------------------------------------------
##ť�O  ��l���ơ���ƳB�z
GDriveJSON = 'question.json'
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc = pygsheets.authorize(service_account_file='question.json') #�ɮ׸̪�google sheet js��
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
#�T�ذ��D����
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
    pre_sheet = data.sample(frac =1,random_state=1) #Random���ø�ƦA��n���D 
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
    #qNum_L = len(sheet["question"])
    return sheet

data_img, data_tail, data_word, data_sen = getSheet(level_L)
sheet = editSheet(data_img) 
##-----------------------------------------------------------------------------------
##�X�D�p�Ѯv  �ܼ�------------------------------------------------
level_Q = 1 # �w�]level 1
qNum_Q = 10 # �C���D�ؼƶq
star_num_Q = 0 #���I
isAsked_Q = False #�X�D�P�_
isChangingLevel_Q = True
isStart_Q = False
index_Q = 0 #�ĴX�D
isInit_Q = True
subindex_Q = index_Q
count_Q = 1
# ��l���ơ���ƳB�z------------------------------------------------
GDriveJSON = 'question.json'
GSpreadSheet_Q = 'cilab_ChatBot_QA'
gc_Q = pygsheets.authorize(service_account_file='question.json')
survey_url_Q = 'https://docs.google.com/spreadsheets/d/1Zf5Qr_dp5GjYZJbxuVKl283fIRKUgs2q9nYNBeTWKJ8/edit#gid=0'
sh_Q = gc_Q.open_by_url(survey_url_Q)
sh_Q.worksheet_by_title('L1_Voc').export(filename='L1_Voc')
sh_Q.worksheet_by_title('L1_Reading').export(filename='L1_Reading')
sh_Q.worksheet_by_title('L1_Cloze').export(filename='L1_Cloze')
sh_Q.worksheet_by_title('L2_Voc').export(filename='L2_Voc')
sh_Q.worksheet_by_title('L2_Reading').export(filename='L2_Reading')
sh_Q.worksheet_by_title('L2_Cloze').export(filename='L2_Cloze')
sh_Q.worksheet_by_title('L3_Voc').export(filename='L3_Voc')
sh_Q.worksheet_by_title('L3_Reading').export(filename='L3_Reading')
sh_Q.worksheet_by_title('L3_Cloze').export(filename='L3_Cloze')

L1_Voc = pd.read_csv('L1_Voc.csv') #type: <class 'pandas.core.frame.DataFrame'>
L1_Reading = pd.read_csv('L1_Reading.csv')
L1_Cloze = pd.read_csv('L1_Cloze.csv')
L2_Voc = pd.read_csv('L2_Voc.csv') 
L2_Reading = pd.read_csv('L2_Reading.csv') 
L2_Cloze = pd.read_csv('L2_Cloze.csv')
L3_Voc = pd.read_csv('L3_Voc.csv') 
L3_Reading = pd.read_csv('L3_Reading.csv') 
L3_Cloze = pd.read_csv('L3_Cloze.csv')
#�T�ذ��D����
def getSheetQA(Qlevel):   
    if(Qlevel == 3):
        sheet_Voc = L3_Voc
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze 

    elif(Qlevel == 2):
        sheet_Voc = L2_Voc
        sheet_Reading = L2_Reading
        sheet_Cloze = L2_Cloze
    else:
        sheet_Voc = L1_Voc
        sheet_Reading = L1_Reading
        sheet_Cloze = L1_Cloze

    return sheet_Voc, sheet_Reading, sheet_Cloze

def editSheetQA(data):
    pre_sheet = data.sample(frac =1,random_state=1) #Random���ø�ƦA��n���D 
    question = pre_sheet.iloc[:,0]
    option1 = pre_sheet.iloc[:,1]
    option2 = pre_sheet.iloc[:,2]
    option3 = pre_sheet.iloc[:,3]
    answer = pre_sheet.iloc[:,4]
    try:
        article = pre_sheet.iloc[:,5]
        sheet_Q = {
            "question": question,
            "option1": option1,
            "option2": option2,
            "option3": option3,
            "answer": answer,
            "article": article
        }
    except:
        sheet_Q = {
            "question": question,
            "option1": option1,
            "option2": option2,
            "option3": option3,
            "answer": answer
        }
    #qNum_Q = len(sheet_Q["question"])
    return sheet_Q

data_Voc, data_Reading, data_Cloze = getSheetQA(level_Q)
sheet_Q = editSheetQA(data_Reading)
#------½Ķ�ܼ�----------------------------
isAsked_T = True
isChangingTrans = True
isEnded = False
TransType = 1 #(ETC= 1, CTE =2)
#-------�o���ܼ�-------------------------
level_S = 1 # �w�]level 1
type_S = 1 # 3���D������
qNum = 10 # �C���D�ؼƶq
star_num = 0 #���I
isAsked_S = False #�X�D�P�_
isChangingLevel_S = True
isStart_S = False
index_S = 0 #�ĴX�D
isInit_S = True
subindex = 0
speech = False
stt_mes = ''
count_S = 1
QA_ = []
#---------------user_score------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
client = gspread.authorize(creds)
spreadSheet = client.open("user_score")
user_sheet = spreadSheet.worksheet("user_score")
user_data = user_sheet.get_all_values()
print('!!!!!!!!!!!!!!!!!!user:', user_data)

##------------------------------------------------
#--------------���D��----------------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
client = gspread.authorize(creds)
spreadSheet = client.open("user_score")
L1_voc_sheet = spreadSheet.worksheet("L1_voc")
L1_voc_data = L1_voc_sheet.get_all_values()
L1_qa = random.sample(L1_voc_data, 5)
L1_sen_sheet = spreadSheet.worksheet("L1_sen")
L1_sen_data = L1_sen_sheet.get_all_values()
L1_qa.extend(random.sample(L1_sen_data, 5))
L2_voc_sheet = spreadSheet.worksheet("L2_voc")
L2_voc_data = L2_voc_sheet.get_all_values()
L2_qa = random.sample(L2_voc_data, 5)
L2_sen_sheet = spreadSheet.worksheet("L2_sen")
L2_sen_data = L2_sen_sheet.get_all_values()
L2_qa.extend(random.sample(L2_sen_data, 5))
L3_voc_sheet = spreadSheet.worksheet("L3_voc")
L3_voc_data = L3_voc_sheet.get_all_values()
L3_qa = random.sample(L3_voc_data, 5)
L3_sen_sheet = spreadSheet.worksheet("L3_sen")
L3_sen_data = L3_sen_sheet.get_all_values()
L3_qa.extend(random.sample(L3_sen_data, 5))
print('L1_qa: ', L1_qa)
print('L2_a: ', L2_qa)
print('L3_qa: ', L3_qa)

#-------------------�d�ݿn���ܼ�-------------------
check_grade = True
choose = '0'

##------------------------------------------------
# ��ť�Ҧ��Ӧ� /callback �� Post Request
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
#----------�B�z�T��--------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global trans, quiz, listen, stt, grade, speech
    global user_index, data_row
    global user_data
    global score, qa_score, lis_score, trans_score, speech_score, game_score, function_status
    global check, check_user, strat_S
    global user_sheet
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
    client = gspread.authorize(creds)
    spreadSheet = client.open("user_score")
    user_sheet = spreadSheet.worksheet("user_score")
    user_data = user_sheet.get_all_values()
    #-------�M��user data--------------------
    for i in range(1,len(user_data)):
        if (user_data[i][0] == event.source.user_id):
            check_user = True
            user_index = i + 1
            break
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
        user_sheet.update_cell(user_index, 8, '1')
        user_data.append([event.source.user_id, 'null', 0, 0, 0, 0, 0, 1])
    #---------------------------------------
    #----------------------��ϥΎ͸��------------------------------
    data_row = user_index - 1
    function_status = user_data[data_row][1]
    score = int(user_data[data_row][2])
    qa_score = int(user_data[data_row][3])
    lis_score = int(user_data[data_row][4])
    speech_score = int(user_data[data_row][5])
    game_score = int(user_data[data_row][6])
    start_S = int(user_data[data_row][7])
    check_user = False
    ############################################
    if event.message.type == 'text':
        if(event.message.text == 'translation'):
            function_status = 'translation'
            user_data[data_row][1] = 'translation'
            user_sheet.update_cell(user_index, 2, 'translation')
            print('translation trans True')
        elif(event.message.text == 'quiz'):
            function_status = 'quiz'
            user_data[data_row][1] = 'quiz'
            user_sheet.update_cell(user_index, 2, 'quiz')
            print('quiz trans True')
        elif(event.message.text == 'listen'):
            function_status = 'listen'
            user_data[data_row][1] = 'listen'
            user_sheet.update_cell(user_index, 2, 'listen')
            print('listen trans True')
        elif(event.message.text == 'speech'):
            function_status = 'speech'
            user_data[data_row][1] = 'speech'
            user_sheet.update_cell(user_index, 2, 'speech')
            print('stt trans True')
        elif(event.message.text == 'score'):
            function_status = 'score'
            user_data[data_row][1] = 'score'
            user_sheet.update_cell(user_index, 2, 'score')
            print('grade trans True')
        function_status = user_data[data_row][1]
        print('!!!!!-------status--------!!!!!: ', function_status)
    #-----------�X�D�B�z�T��-----------------
        if(function_status == 'quiz'):
            global isAsked_Q,isInit_Q
            global index_Q
            global isChangingLevel_Q
            global sheet_Q,subindex_Q
            replytext = event.message.text
            myId = event.source.user_id
            if event.message.type == 'text':   
                if(isInit_Q == True or replytext =='?'):
                    isChangingLevel_Q = True
                    message = TextSendMessage(text="�w��Ө���D�p�F�H�I\n\n�b�o��i�H��ܾA�X�A�������רӬD�ԡA�@���D�ئ�10�D�C\n\n�D�ؤ������J�D�B�J�|�r�H�ξ\Ū����A���D�V��T��o���P�P�ƶV�h�@�I\n\n�Ĥ@���N����G??\n�ĤG���~����G?\n�ĤT���~����G?")
                    line_bot_api.push_message(myId, message)
                    isInit_Q=False
                if(isChangingLevel_Q == True):   
                    isAsked_Q = False
                    setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/V5TmMA.png','���D�p�F�H','�Q�n�ۧ��˴��ǲ߭^���?')
                    line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
                elif isStart_Q == True:
                    if( isAsked_Q == False ): 
                        isAsked_Q = True
                        QA_bubble = Question_Q()
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
#--------------ť�O�B�z�T��--------------------
        elif(function_status == 'listen'):
            global isAsked_L,isInit_L
            global index_L
            global isChangingLevel_L
            global sheet,subindex
            replytext = event.message.text
            myId = event.source.user_id
            if event.message.type == 'text':   
                if(isInit_L == True or replytext =='?'):
                    isChangingLevel_L = True
                    message = TextSendMessage(text="�w��Ө�ť�O�m�ߡI\n\n�b�o��i�H��ܾA�X�A�������סC\n\n�D�ؤ����o���B���J�H�Υy�l�A���D�V��T��o���P�P�ƶV�h�@�I\n\n�Ĥ@���N����G??\n�ĤG���~����G?\n�ĤT���~����G?")
                    line_bot_api.push_message(myId, message)
                    isInit_L=False
                if(isChangingLevel_L == True):   
                    isAsked_L = False
                    setlevel_bubble = levelBubble('https://upload.cc/i1/2020/06/08/jhziMK.png','ť�O�m��','�`�Oť�����O�H�b�������?')
                    line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
                elif isStart_L == True:
                    if( isAsked_L == False ): 
                        isAsked_L = True
                        QA_bubble = Question()
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(event.reply_token, message)
#----------------½Ķ�B�z�T��---------------
        elif(function_status == 'translation' and event.message.text != 'translation'):
            myId = event.source.user_id
            global isAsked_T, isChangingTrans, isEnded
            replytext = event.message.text
            if event.message.type == 'text':   
                if replytext =='?':
                    isChangingTrans = True
                    isEnded = False

                if (isChangingTrans == True ):  
                    isAsked_T = True
                    isEnded = False
                    buttons_template = TemplateSendMessage (
                        alt_text = 'Buttons Template',
                        template = ButtonsTemplate (
                            title = '½Ķ�p�F�H',
                            text = '������n������½Ķ����?',
                            thumbnail_image_url='https://upload.cc/i1/2020/07/01/IV2yHq.png',
                            actions = [
                                    PostbackTemplateAction(
                                        label = "�^��½����", 
                                        #text = "�^��½����",
                                        data = 'ETC'
                                    ),
                                    PostbackTemplateAction(
                                        label = "����½�^��",
                                        #text = "����½�^��",
                                        data = 'CTE'
                                    )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, buttons_template)
                    
                elif( isAsked_T == False ):  
                    translatedMessage = translation(replytext)
                    print("tenasM = ",translatedMessage)
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text = translatedMessage))

                    Translation_bubble = Choose_NextStep()
                    message2 = FlexSendMessage(alt_text="Translation_bubble", contents = Translation_bubble)
                    line_bot_api.push_message(myId, message2)
                    isAsked_T = True 
                else:
                    if(isEnded == True):
                        #isAsked_T = True
                        message = "���§A�ϥ�½Ķ�p�F�H~~\n�w���I�}�U����A�ϥΨ�L�\��@�I"
                        #line_bot_api.reply_message(event.reply_token,message)
    #---------------------�o���B�z�T��------------------
        elif(function_status == 'speech'):
            global index_S, QA_
            global stt_mes
            myId = event.source.user_id
            if(start_S == 1):
                message = TextSendMessage(text="�w��Ө�o���m�ߡI\n\n�b�o���m�߸̡A�A�i�H��ܽm�ߤ��P�����ת��o���A�@���D�ط|��10�D�I\n\n�D�ؤ������J�P�y�l��������A�V������N�i�H��o��h�P�P�@�I\n\n�Ĥ@���N����G??\n�ĤG���~����G?\n�ĤT���~����G?")
                line_bot_api.push_message(myId, message)
                setlevel_bubble = levelBubble('https://upload.cc/i1/2020/05/18/zaHN8Q.jpg','�o���m��','�ᤣ�X���T���o����?')
                line_bot_api.reply_message(event.reply_token, setlevel_bubble)  
#----------------�n���B�z�T��------------------
        elif(function_status == 'score'):
            score_bubble = total_score()
            message = FlexSendMessage(alt_text="score_bubble", contents = score_bubble)
            line_bot_api.reply_message(event.reply_token, message)

#------------�y���B�z�T��----------------
"""
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    global trans, quiz, listen, stt, grade, speech, stt_mes, star_num, OA_
    global index_S, count_S, score, speech_score
    qNum_S = 10
    if(function_status == 'speech'):
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
            t = '���T�����D'+test+str(e.args)+path
            wrongBubble = tryagainBubble('�ЦA�ո�!!', '�٦��Ǥ����T�@~�A�A�ոլݡI', 'tryagain')
            message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
            line_bot_api.reply_message(event.reply_token,message)
        os.remove(path)
        text = r.recognize_google(audio,language='zh-CN')
        stt_mes = text
        print('�y���T���G', stt_mes)
        print('�y���B�z QA_[index_S][1]', QA_[index_S][1])
        if(index_S < qNum_S): #���������D�w�ƥ�
            if(stt_mes != QA_[index_S][1]):
                if(count_S != 0):
                    wrongBubble = tryagainBubble('�ЦA�ո�!!', '�٦��Ǥ����T�@~�A�A�ոլݡI', 'tryagain')
                    message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    count_S -= 1
                elif(count_S == 0):
                    if(index_S == 9):
                        loseBubble = finalBubble('�A���A�F!!', '�n�i���@!\n���W�ƦAť�@�����T�o���a!')
                        user_sheet.update_cell(user_index, 8, 1)
                    else:
                        loseBubble = loseBubble = nextBubble('�n�i���@!\n���W�ƦAť�@�����T�o���a!','�A���A�F!!')
                    message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    count_S = 1
                    index_S += 1
            else:
                star_num += count_S
                score += count_S
                speech_score += count_S
                print('score: ', score)
                print('speech_score: ', speech_score)
                user_sheet.update_cell(user_index, 3, score)
                user_sheet.update_cell(user_index, 6, speech_score)
                print('save!!!!!!!!!!')
                print('���T����!')
                if(count_S == 1):
                   reply = '�A�n��!�@���N����F!'
                elif(count_S == 0):
                    reply = '�n�ή@!�A����F!'
                print(count_S, reply)
                if(index_S == 9):
                    reply = '�n�ή@!�A����F!'
                    correctBubble = finalBubble('���ߵ���!!', reply)
                    user_sheet.update_cell(user_index, 8, 1)
                else:
                    correctBubble = rightBubble(reply)
                message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                line_bot_api.reply_message(event.reply_token,message)
                index_S += 1
                count_S = 1
"""
#-----------------�y���B�z�T������----------------


#�X�D�p�Ѯv  �^�X�P�_------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    global trans, quiz, listen, stt, score, qa_score, lis_score, trans_score, speech_score, game_score, function_status
    print('event.postback.data:', event.postback.data)
    if(function_status == 'quiz'):
        print("---Feedback---")
        global isAsked_Q,isStart_Q,isChangingLevel_Q
        global index_Q,sheet_Q,subindex_Q
        global qNum_Q, star_num_Q
        global data_Voc, data_Reading, data_Cloze, count_Q
        myId = event.source.user_id
        print("postbackData = ",event.postback.data )
        if(isChangingLevel_Q==True):
            level_bubble = setLevel_Q(event.postback.data) 
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 

        elif(event.postback.data == "start"):  
            print("******index_Q index_Q%8 count_Q",index_Q,index_Q%8,count_Q)
            if(index_Q == 7 and count_Q == 1):
                print("article!?")
                sheet_article = editSheetQA(data_Reading) 
                QA_bubble_article = QA_Bubble.Article(sheet_article,subindex_Q)
                article = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble_article)
                line_bot_api.push_message(myId, article)

            isStart_Q = True

        elif(isStart_Q == True): 
            correctAns = str(sheet_Q["answer"][subindex_Q])
            print("correct answer = ",correctAns)
            print("answer index_Q = ", index_Q)
            print("answer subindex_Q = ", subindex_Q)
            answer = event.postback.data
            if(index_Q < qNum_Q): #���������D�w�ƥ�
                print('count_Q: ', count_Q)
                if answer != correctAns:
                    if(count_Q != 0):
                        isStart_Q = False
                        wrongBubble = tryagainBubble('�ЦA�ո�!!', '�٦��Ǥ����T�@~�A�A�ոլݡI', 'start')
                        message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        count_Q -= 1
                    elif(count_Q == 0):
                        isStart_Q = False
                        if(index_Q == 9):
                            loseBubble = finalBubble('�A���A�F!!', '�n�i���@~���׬O(' + answer + ')�~��@!')
                        else:
                            loseBubble = nextBubble('�n�i���@~���׬O(' + answer + ')�~��@!','�A���A�F!!')
                        message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        count_Q = 1
                        index_Q += 1
                    isAsked_Q = False
                else:
                    isStart_Q = False
                    star_num_Q += count_Q
                    score += count_Q
                    qa_score += count_Q
                    print('score: ', score)
                    print('qa_score: ', qa_score)
                    user_sheet.update_cell(user_index, 3, score)
                    user_sheet.update_cell(user_index, 4, qa_score)
                    print('save!!!!!!!!!!')
                    print('���T����!')
                    if(count_Q == 1):
                        reply = '�A�n��!�@���N����F!'
                    elif(count_Q == 0):
                        reply = '�n�ή@!�A����F!'
                    print(count_Q, reply)
                    if(index_Q == 9):
                        print("last Q")
                        reply = '�n�ή@!�A����F!'
                        correctBubble = finalBubble('���ߵ���!!', reply)
                    else:
                        correctBubble = rightBubble(reply)
                    message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    index_Q += 1
                    if(index_Q < 10):
                        isAsked_Q = False
                    count_Q = 1
                print('after count_Q: ', count_Q)
                print('after index_Q: ', index_Q)
        
        elif(event.postback.data == "end"):
            starBubble = totalStarBubble()
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
            isStart_Q = False

        elif (event.postback.data == "next"): 
            index_Q = 0
            star_num_Q = 0
            print("���D������ܧ� �ϼƩM�����k�s----",index_Q,star_num_Q)
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)  

        elif (event.postback.data == "changeLevel"): 
            isChangingLevel_Q = True

        elif (event.postback.data == "next2"):
            isStart_Q = True
            print("restart isAsked_Q",isAsked_Q)
            print("restart QA_bubble")
            isAsked_Q = True
            QA_bubble = Question_Q()
            message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
            line_bot_api.reply_message(event.reply_token, message)
#------------------ť�O�^�X�P�_-------------------
    elif(function_status == 'listen'):
        print("---Feedback---")
        global isAsked_L,isStart_L,isChangingLevel_L
        global index_L,sheet,subindex_L
        global qNum_L, star_num_L
        global data_img, data_tail, data_word, data_sen, count_L

        if(isChangingLevel_L==True):
            level_bubble = setLevel(event.postback.data) 
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 

        elif(event.postback.data == "start"):  
            isStart_L = True
        elif(isStart_L == True): 
            correctAns = str(sheet["answer"][subindex_L])
            print("correct answer = ",str(sheet["answer"][subindex_L]))
            print("answer index_L = ", index_L)
            print("answer subindex_L = ", subindex_L)
            answer = event.postback.data
            if(index_L < qNum_L): #���������D�w�ƥ�
                print('count_L: ', count_L)
                print('index_L: ', index_L)
                if answer != str(sheet["answer"][subindex_L]):
                    #feedback = sheet["feedback"][subindex_L]
                    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
                    if(count_L != 0):
                        isStart_L = False
                        wrongBubble = tryagainBubble('�ЦA�ո�!!', '�٦��Ǥ����T�@~�A�A�ոլݡI', 'start')
                        message = FlexSendMessage(alt_text="wrongBubble", contents = wrongBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        count_L -= 1
                    elif(count_L == 0):
                        isStart_L = False
                        if(index_L == 9):
                            loseBubble = finalBubble('�A���A�F!!', '�n�i���@~���׬O(' + answer + ')�~��@!')
                        else:
                            loseBubble = nextBubble('�n�i���@~���׬O(' + answer + ')�~��@!','�A���A�F!!')
                        message = FlexSendMessage(alt_text="loseBubble", contents = loseBubble)
                        line_bot_api.reply_message(event.reply_token,message)
                        count_L = 1
                        index_L += 1
                    isAsked_L = False
                else:
                    isStart_L = False
                    star_num_L += count_L
                    score += count_L
                    lis_score += count_L
                    print('score: ', score)
                    print('lis_score: ', lis_score)
                    user_sheet.update_cell(user_index, 3, score)
                    user_sheet.update_cell(user_index, 5, lis_score)
                    print('save!!!!!!!!!!')
                    print('���T����!')
                    if(count_L == 1):
                        reply = '�A�n��!�@���N����F!'
                    elif(count_L == 0):
                        reply = '�n�ή@!�A����F!'
                    print(count_L, reply)
                    if(index_L == 9):
                        reply = '�n�ή@!�A����F!'
                        correctBubble = finalBubble('���ߵ���!!', reply)
                    else:
                        correctBubble = rightBubble(reply)
                    message = FlexSendMessage(alt_text="correctBubble", contents = correctBubble)
                    line_bot_api.reply_message(event.reply_token,message)
                    index_L += 1
                    if(index_L < 10):
                        isAsked_L = False
                    count_L = 1
                print('after count_L: ', count_L)
                print('after index_L: ', index_L)
        
        elif(event.postback.data == "end"):
            #print('���ߧA�����o����ť�O�m�ߤF!star=',star_num_L)
            starBubble = totalStarBubble()
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
            isStart_L = False

        elif (event.postback.data == "next"): 
            index_L = 0
            star_num_L = 0
            print("���D������ܧ� �ϼƩM�����k�s----",index_L,star_num_L)
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)  

        elif (event.postback.data == "changeLevel"): 
            isChangingLevel_L = True

        elif (event.postback.data == "next2"):
            isStart_L = True
            print("restart isAsked_L",isAsked_L)
            print("restart QA_bubble")
            isAsked_L = True
            QA_bubble = Question()
            message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
            line_bot_api.reply_message(event.reply_token, message)
#-----------------½Ķ�^�X�P�_-------------------
    elif(function_status == 'translation'):
        print("---Feedback---")
        global isAsked_T,TransType,isChangingTrans,isEnded
        levelinput = event.postback.data
        if(isChangingTrans==True):
            isChangingTrans = False
            if (levelinput=='ETC'):
                TransType = 1
                print("�����^½���Ҧ�")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "�ثe���� �^��½����Ҧ��I\n�бN�A�Q½Ķ���^���r�Υy�l�ǰe���ڮ@~"))
                isAsked_T = False

            elif (levelinput=='CTE'):
                TransType = 2
                print("������½�^�Ҧ�")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "�ثe���� ����½�^��Ҧ��I\n�бN�A�Q½Ķ������r���Υy�l�ǰe���ڮ@~"))
                isAsked_T = False   
            else:       
                isChangingTrans = True
                isAsked_T = True
            
        if(levelinput == 'Next'):
            if(isEnded == False):
                if(TransType == 1):
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "�жǰe�^���r�Υy�l~"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "�жǰe����r���Υy�l~"))
        
                isAsked_T = False
        
        if(levelinput == 'End'):
            isEnded = True
            isAsked_T = True  
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "���§A�ϥ�½Ķ�p�F�H~~\n�w���I�}�U����A�ϥΨ�L�\��@�I"))
#-----------------�y���^�X�P�_----------------------------------------
"""
    elif(function_status == 'speech'):
        global stt_mes, speech, star_num, QA_
        print("---Feedback---")
        global isAsked_S,isStart_S
        global index_S, count_S
        if(event.postback.data == 'L' or event.postback.data == 'M' or event.postback.data == 'H'):
            level_bubble = setLevel_S(event.postback.data)
            message = FlexSendMessage(alt_text="level_bubble", contents = level_bubble)
            line_bot_api.reply_message(event.reply_token,message) 
        elif(event.postback.data == "start"):
            speech_bubble = QA_S(QA_[index_S][0], QA_[index_S][1])
            message = FlexSendMessage(alt_text="speech_bubble", contents = speech_bubble)
            line_bot_api.reply_message(event.reply_token, message)
        elif(event.postback.data == "end"):
            starBubble = totalStarBubble()
            message = FlexSendMessage(alt_text="starBubble", contents = starBubble)
            line_bot_api.reply_message(event.reply_token,message)
        elif (event.postback.data == "next"): 
            index_S = 0
            star_num = 0
            changelevel_bubble = changeLevelBubble()
            message = FlexSendMessage(alt_text="changelevel_bubble", contents = changelevel_bubble)
            line_bot_api.reply_message(event.reply_token, message)  

        elif (event.postback.data == "changeLevel"): 
            isChangingLevel_L = True
        elif (event.postback.data == "next2"):
            isStart_S = True
            isAsked_S = True
        elif(event.postback.data == "tryagain"):
            speech = True
"""
##�X�D�p�Ѯv  �]�wLevel------------------------------------------------
def setLevelQA(levelinput):
    print("---Changing Level---")
    global sheetQA, data_Word, data_Grammar, data_Cloze
    global qNumQA
    global level
    global isChangingLevel,isChangingType
   
    if (levelinput=='L'):
        level = 1
        isChangingLevel = False
        isChangingType = True
        myResult= ("�ثe�{�פ����ܪ��")
        
    elif (levelinput=='M'):
        level = 2
        isChangingLevel = False
        isChangingType = True
        myResult= ("�ثe�{�פ����ܤ���")    
    elif (levelinput=='H'):
        level = 3
        isChangingLevel = False
        isChangingType = True
        myResult= ("�ثe�{�פ����ܰ���")  
    else:       
        isChangingLevel = True
        myResult = "N"
    
    if isChangingLevel == False:
        data_Word, data_Grammar, data_Cloze = getSheetQA(level)
      
    return myResult
##�X�D�p�Ѯv  �]�w�X�D����------------------------------------------------
def setTypeQA(typeinput) :
    print("---Changing Level---")
    global sheetQA, qNumQA
    global isChangingType
    
    if (typeinput=='W'):
        sheetQA, qNumQA = editSheetQA(data_Word) 
        isChangingType = False
        myResult= ("�D�����������ܵ��J�m��")
        
    elif (typeinput=='G'):
        sheetQA, qNumQA = editSheetQA(data_Grammar) 
        isChangingType = False
        myResult= ("�D�����������ܤ�k�m��")    
    elif (typeinput=='C'):
        sheetQA, qNumQA = editSheetQA(data_Cloze) 
        isChangingType = False
        myResult= ("�D�����������ܧJ�|�r�m��")  
    else:       
        isChangingType = True
        myResult = "N"
    
    return myResult
##�X�D�p�Ѯv  �X�D�������------------------------------------------------
def typeButtonQA():
    QAsort_bubble = BubbleContainer (
                header = BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text='�п���D������', weight='bold', size='xl', color = '#000000')                   
                    ]
                ),
                body = BoxComponent(
                    layout='vertical',
                    contents=[
                        ButtonComponent(
                            action = PostbackAction(label = '���J�m��', data = 'W', text = '���J�m��'),
                            color = '#001774',
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '��k�m��', data = 'G', text = '��k�m��'),
                            color = '#FF595D',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        ),
                        ButtonComponent(
                            action = PostbackAction(label = '�J�|�r�m��', data = 'C', text = '�J�|�r�m��'),
                            color = '#FFB54A',
                            margin = 'md',           
                            style = 'primary',
                            gravity = 'center'
                        )
                    ]
                )
            )   
            
    return QAsort_bubble

def setLevel_Q(levelinput):
    print("---Changing Level---")
    global data_Voc, data_Reading, data_Cloze
    global level_Q
    global isChangingLevel_Q
    
    if (levelinput=='L'):
        level_Q = 1
        myResult = readyBubble(level_Q)
        isChangingLevel_Q = False
        
    elif (levelinput=='M'):
        level_Q = 2
        myResult = readyBubble(level_Q)    
        isChangingLevel_Q = False

    elif (levelinput=='H'):
        level_Q = 3
        myResult = readyBubble(level_Q)
        isChangingLevel_Q = False

    else:       
        isChangingLevel_Q = True
        myResult = "N"

    if isChangingLevel_Q == False:
        data_Voc, data_Reading, data_Cloze = getSheetQA(level_Q)
        #sheet_Q = editSheet(pre_sheet)
        print("�������׫� ��s���o�s���H���D��----level_Q get sheet_Q",sheet_Q)
      
    return myResult

def Question_Q():
    global subindex_Q,sheet_Q
    print("�粒���Ŷ}�l�X�D")
    print("index_Q",index_Q)
    print("subindex_Q = ", subindex_Q)
    if index_Q < 3:
        subindex_Q = index_Q
        sheet_Q = editSheetQA(data_Voc)
        QA_bubble = QA_Bubble.Voc(sheet_Q,index_Q,subindex_Q)
    elif index_Q < 7:
        subindex_Q = index_Q - 3
        sheet_Q = editSheetQA(data_Cloze)
        QA_bubble = QA_Bubble.Cloze(sheet_Q,index_Q,subindex_Q)
    else:
        subindex_Q = index_Q - 7
        sheet_Q = editSheetQA(data_Reading) 
        QA_bubble = QA_Bubble.Reading(sheet_Q,index_Q,subindex_Q)
    return QA_bubble
#----------ť�Ofunction------------------
#�]�wLevel------------------------------------------------
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
        print("�������׫� ��s���o�s���H���D��----level_L get sheet",sheet)
      
    return myResult

def Question():
    global subindex_L,sheet
    print("�粒���šI�}�l�X�D")
    print("index_L",index_L)
    if index_L < 3:
        if level_L != 3:
            sheet = editSheet(data_tail)
            QA_bubble = QA.QA_Tail(sheet,index_L,index_L)
        else: #���ūe�T�D�A�D�ؤ��P
            print("*****change ���")
            sheet = editSheet(data_sen) 
            QA_bubble = QA.QA_Sentence(sheet,index_L,subindex_L,'�̾ڭ��ɡA��X�̾A��������')
    elif index_L < 7:
        subindex_L = index_L-3
        sheet = editSheet(data_word)
        QA_bubble = QA.QA_Word(sheet,index_L,subindex_L)
    else:
        subindex_L = index_L-7
        sheet = editSheet(data_sen) 
        QA_bubble = QA.QA_Sentence(sheet,index_L,subindex_L,'��X���T������y�l')
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
                                    label = "���", 
                                    text = "���",
                                    data = 'L'
                                ),
                                PostbackTemplateAction(
                                    label = "����",
                                    text = "����",
                                    data = 'M'
                                ),
                                PostbackTemplateAction(
                                    label = "����",
                                    text = "����",
                                    data = 'H'
                                )
                        ]
                    )
                )
    return level_template

def readyBubble(level):
    if level == 1:
        leveltext = '��������סI'
    elif level == 2:
        leveltext ='���������סI'
    else:
        leveltext ='���������סI'
    print("leveltext",leveltext)   
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="�ǳƦn�F��?", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="�A��ܪ��O" + leveltext, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '�}�l���D', data = 'start', text = '�}�l���D'),
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
                TextComponent(text="��o�P�P!!", weight='bold', size='xl', align = 'center')                   
            ]
        ),
        hero= ImageComponent(
            url="https://upload.cc/i1/2020/07/01/pDbGXh.png", size='full', aspect_ratio="1.51:1",aspect_mode="cover"
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="���ߧA��o�F" + str(star_num_L) + "���P�P!" , size='xs', align = 'center'),
                SeparatorComponent(margin='md'),
                ButtonComponent(
                    action = PostbackAction(label = "�U�@�j�D", data = 'next', text = "�U�@�j�D"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "�ڤ����F", data = 'end', text = "�ڤ����F"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble

def total_score():
    Bubble = BubbleContainer (
        direction='ltr',
        hero= ImageComponent(
            url="https://upload.cc/i1/2020/06/15/J8dF3o.png", size='full', aspect_ratio="20:13", aspect_mode="cover"
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="�P�P�`��", size='xl', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="�A���P�P�`�ơG",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(score) + "��",flex = 0, margin = 'md', size='lg', color = '#F10000')
                        ]
                ),
                TextComponent(text="���D�p�F�H", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="�A��o���P�P�G",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(qa_score) + "��",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="ť�O�m��", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="�A��o���P�P�G",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(lis_score) + "��",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="�o���m��", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="�A��o���P�P�G",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(speech_score) + "��",flex = 0, margin = 'md', size='sm', color = '#F18200')
                        ]
                ),
                TextComponent(text="�����C��", size='lg', margin = 'md', weight = 'bold'),
                BoxComponent(
                    layout='baseline',
                    margin = 'md',
                    contents=[
                        TextComponent(text="�A��o���P�P�G",flex = 0, margin = 'md', size='sm', color = '#999999'),
                        TextComponent(text=str(game_score) + "��",flex = 0, margin = 'md', size='sm', color = '#F18200')
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
                    action = PostbackAction(label = "��������", data = 'changeLevel', text = "��������"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "���ΡA�~��U�@�j�D", data = 'next2', text = "���ΡA�~��U�@�j�D"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble
##  End------------------------------------------------

#-----------------½Ķfunction--------------------------
def translation(text):
    translator = Translator()
    #lang = translator.detect(event.message.text)
    #print("Lang=",lang.lang)
    if TransType == 2: 
        #if lang.lang == "zh-CN" :
        print("---- transmeaasge C to E -----")
        translateMessage = translator.translate(text, dest='en')
        print("trans =",translateMessage.text)
        #message = TextSendMessage(text=translateMessage.text)
    elif TransType == 1:
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
                                action = PostbackAction(label = '½�U�@�y', data = 'Next', text = None),
                                color = '#F1C175',
                                style = 'primary',
                                gravity = 'center',
                                margin = 'md'
                            ),
                            ButtonComponent(
                                action = PostbackAction(label = '����½Ķ', data = 'End', text = None),
                                color = '#E18876',
                                margin = 'md',           
                                style = 'primary',
                                gravity = 'center'
                            )
                        ]
                    )
                )   
    return Translation_bubble

#-----------------�o��Function------------
def QA_S(address, ques):
    QA_Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="�o���m��("+ str(index_S+1) +"/10)", weight='bold', size='lg', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text= ques, weight='bold', size='xl', align = 'center'),
                TextComponent(text='�гz�L�y���T���ᵹ��ť', margin= 'none',size='sm', align = 'center',gravity = 'center', color= '#727272'),
                SeparatorComponent(margin='xl',color='#A89F9F'),
                ButtonComponent(
                    action = URIAction(label= 'ť���T�o��', uri= address),
                    color = '#3B9A9C',
                    margin = 'lg',
                    style = 'primary',
                    flex = 10
                )
            ]
        )
    )                       
    return QA_Bubble

def setLevel_S(levelinput):
    print("---Changing Level---")
    global QA_, start_S
    
    if (levelinput=='L'):
        QA_ = L1_qa
        myResult = readyBubble(1)
        
    elif (levelinput=='M'):
        QA_ = L2_qa
        myResult = readyBubble(2)

    elif (levelinput=='H'):
        QA_ = L3_qa
        myResult = readyBubble(3)

    else:
        myResult = "N"

    if isChangingLevel_L == False:
        print("��ܦn�������D�ءG ", QA_)
    user_sheet.update_cell(user_index, 8, '0')
    return myResult
#----------------end----------------
#-------------���D�P�_function-------------
def rightBubble(reply): 
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="���ߵ���!!", weight='bold', size='xl', align = 'center')                   
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
                    action = PostbackAction(label = '�U�@�D', data = 'start', text = '�U�@�D'),
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
                TextComponent(text = str1, weight='bold', size='xl', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = str2, size='xs', align = 'center', gravity = 'top'),
            ]  
        ),
        footer = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    action = PostbackAction(label = '�A�դ@��', data = str3, text = '�A�դ@��'),
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
                    action = PostbackAction(label = '���U�@�D', data = 'start', text = '���U�@�D'),
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
                    action = PostbackAction(label = '�����@��', data = 'end', text = '�����@��'),
                    color = '#E15B45',
                    style = 'primary'
                )
            ]

        )
    )  
    return Bubble

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
