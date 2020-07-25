from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
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
import datetime 
import pygsheets
from pydub import AudioSegment
import speech_recognition as sr
import time
import tempfile
from gtts import gTTS
from pygame import mixer

app = Flask(__name__)

line_bot_api = LineBotApi('Ay6xk+FmKxu4tFPtdzXBMR/V8Mf1GnwNi07Vt9QgOHCHwUCd3x8pdRMu7rTHR1/QWlcVcaaHRzfi9gARYXgNqm7WT7M7YoeWJv+NFkl+iZg5K0jAERYZud6HpNmpVXm6TEIf7ZY1DxnH55E77umPawdB04t89/1O/w1cDnyilFU=')

handler = WebhookHandler('533dbc0dab0d92eea7a87b05cb7e49a6')
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
score_row = 0
check_user = False
check = False
#----------------------
##聽力  變數------------------------------------------------
level_L = 1 # 預設level 1
type_L = 1 # 3種題目類型
qNum = 20 # 每輪題目數量
star_num = 0 #集點
isAsked_L = False #出題與否
isChangingLevel_L = True
index_L = 0 #第幾題
subindex = 0
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
##-----------------------------------------------------------------------------------
#四種問題類型
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
##出題小老師  變數------------------------------------------------
level = 1 #預設level 1
star_numQA = 0 #集點
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

#---------------user_score------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
client = gspread.authorize(creds)
spreadSheet = client.open("user_score")
user_sheet = spreadSheet.worksheet("user_score")
user_data = user_sheet.get_all_values()
print('!!!!!!!!!!!!!!!!!!user:', user_data)

def getSheetQA(level):  #打亂該sheet順序，並存成dictionary格式  
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

def editSheetQA(data):
    df = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題   
    print("getSheet df = ",df)
    question = df.iloc[:,0]
    option1 = df.iloc[:,1]
    option2 = df.iloc[:,2]
    option3 = df.iloc[:,3]
    option4 = df.iloc[:,4]
    feedback = df.iloc[:,5]
    answer = df.iloc[:,6]
    sheetQA = {
        "question": question,
        "option1": option1,
        "option2": option2,
        "option3": option3,
        "option4": option4,
        "feedback": feedback,
        "answer": answer
    }
    qNumQA = len(sheetQA["question"])
    return sheetQA,qNumQA

data_Word, data_Grammar, data_Cloze = getSheetQA(level)
sheetQA, qNumQA = editSheetQA(data_Word)
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
#----------處理訊息--------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global trans, quiz, listen, stt, grade
    global user_index
    global score_row,user_data
    global score, qa_score, lis_score
    global check, check_user
    global user_sheet
    #--------------抓user資料----------------
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("./score.json", scope)
    client = gspread.authorize(creds)
    spreadSheet = client.open("user_score")
    user_sheet = spreadSheet.worksheet("user_score")
    user_data = user_sheet.get_all_values()
    #--------------判斷user_id是否已在記錄中----------------
    for i in range(0,len(user_data)):
        if (user_data[i][0] == event.source.user_id):
            check_user = True
            user_index = i
            score = int(user_data[user_index][1])
            qa_score = int(user_data[user_index][2])
            lis_score = int(user_data[user_index][3])
            break
    #-------------若沒有則在資料庫中增加一筆user data-------------
    if (check_user == False):
        user_index = len(user_data)
        score_row = user_index + 1
        user_sheet.add_rows(1)
        user_sheet.update_cell(3, 1, event.source.user_id)
        user_sheet.update_cell(3, 2, '0')
        user_sheet.update_cell(3, 3, '0')
        user_sheet.update_cell(3, 4, '0')
        user_data.append([id, 0, 0, 0])
        score = int(user_data[user_index][1])
        qa_score = int(user_data[user_index][2])
        lis_score = int(user_data[user_index][3])
    check_user = False
    score_row = user_index + 1
    #------------user data 處理設定完畢-------------------
    ############################################
    if event.message.type == 'text':
        if(event.message.text == 'translation'):
            trans = True
            quiz = False
            listen = False
            stt = False
            grade = False
            print('translation trans True')
        elif(event.message.text == 'quiz'):
            quiz = True
            trans = False
            listen = False
            stt = False
            grade = False
            print('quiz trans True')
        elif(event.message.text == 'listen'):
            listen = True
            trans = False
            quiz = False
            stt = False
            grade = False
            print('listen trans True')
        elif(event.message.text == 'speech'):
            stt = True
            listen = False
            trans = False
            quiz = False
            grade = False
            print('stt trans True')
        elif(event.message.text == 'score'):
            grade = True
            stt = False
            listen = False
            trans = False
            quiz = False
            print('grade trans True')
    #-----------出題處理訊息-----------------
        if(quiz == True):
            global isAsked
            global index
            global isChangingLevel
            global sheetQA
            replytext = event.message.text 
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
                QAsort_bubble = typeButtonQA()
                message = FlexSendMessage(alt_text="QAsort_bubble", contents = QAsort_bubble)
                line_bot_api.reply_message(event.reply_token,message) 
                
            else:
                if( isAsked == False ):                  
                    question = sheetQA["question"][index]
                    print(question)
                    print("1:", sheetQA["option1"][index], "\n2:", sheetQA["option2"][index], "\n3:", sheetQA["option3"][index],
                            "\n4:", sheetQA["option4"][index], "\n")
                    isAsked = True
                    
                    QA_BubbleContainer = BubbleContainer (
                        direction='ltr',
                        header = BoxComponent(
                            layout='vertical',
                            contents=[
                                TextComponent(text=question, size='lg', align = 'start',gravity='top')                   
                            ]
                        ),
                        body = BoxComponent(
                            layout='vertical',
                            contents=[
                                ButtonComponent(
                                    action = PostbackAction(label = "1. " +sheetQA["option1"][index], data = '1', text = "1. " +sheetQA["option1"][index]),
                                    color = '#46549B',
                                    margin = 'md',
                                    style = 'primary'
                                ),
                                    ButtonComponent(
                                    action = PostbackAction(label = "2. " +sheetQA["option2"][index], data = '2', text = "2. " +sheetQA["option2"][index]),
                                    color = '#7E318E',
                                    margin = 'md',
                                    style = 'primary'
                                ),
                                    ButtonComponent(
                                    action = PostbackAction(label = "3. " +sheetQA["option3"][index], data = '3', text = "3. " +sheetQA["option3"][index]),
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
    #--------------聽力處理訊息--------------------
        elif(listen == True):
            global isAsked_L
            global index_L
            global isChangingLevel_L
            global sheet,subindex
            replytext = event.message.text
            #myId = event.source.user_id
            if event.message.type == 'text':   
                if (isChangingLevel_L == True or replytext =='?'):   
                    isChangingLevel_L = True
                    isAsked_L = False
                    buttons_template = TemplateSendMessage (
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
                    line_bot_api.reply_message(event.reply_token, buttons_template)  
                else:
                    if( isAsked_L == False ):   
                        print("選完階級！")
                        isAsked_L = True
                        print("index_L",index_L)
                        subindex = index_L%5
                        print("subindex = ",subindex)
                        if index_L < 5:
                            sheet = editSheet(data_img)
                            QA_bubble = QA.QA_Img(sheet,index_L,subindex)
                        elif index_L < 10:
                            sheet = editSheet(data_tail)
                            QA_bubble = QA.QA_Tail(sheet,index_L,subindex)
                        elif index_L < 15:
                            sheet = editSheet(data_word)
                            QA_bubble = QA.QA_Word(sheet,index_L,subindex)
                        else:
                            sheet = editSheet(data_sen) 
                            QA_bubble = QA.QA_Sentence(sheet,index_L,subindex)    
                    
                        message = FlexSendMessage(alt_text="QA_bubble", contents = QA_bubble)
                        line_bot_api.reply_message(
                            event.reply_token,
                            message
                        )
    #----------------翻譯處理訊息---------------
        elif(trans == True and event.message.text != 'translation'):
            translator = Translator()
            if event.message.type == 'text':
                lang = translator.detect(event.message.text)
                print("Lang=",lang.lang)
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
                    message = TextSendMessage(text="I can't translate this kind of message")
            else:
                message = TextSendMessage(text="I can't translate this kind of message")
            print("message=",message)
            line_bot_api.reply_message(event.reply_token, message)
            
            print("=======Reply Token=======")
            print(event.reply_token)
            print("=========================")

#----------------積分處理訊息------------------
        elif(grade == True):
            global choose, check_grade
            print('check_grade: ', check_grade)
            print('choose:', choose)
            if event.message.type == 'text':
                if(event.message.text == '1'):
                    choose = '1'
                elif(event.message.text == '2'):
                    choose = '2'
                elif(event.message.text == '3'):
                    choose = '3'
            if(check_grade == True):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請問想查看哪項積分?\n1. 總分\n2. 解題小達人積分\n3.聽力練習積分\n'))
                check_grade = False
            if(choose == '1'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '總分為: ' + str(score)))
                choose = '0'
                check_grade = True
            elif(choose == '2'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '解題小達人積分為: ' + str(qa_score)))
                choose = '0'
                check_grade = True
            elif(choose == '3'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '聽力練習積分為: ' + str(lis_score)))
                choose = '0'
                check_grade == True

#------------語音處理訊息----------------
@handler.add(MessageEvent,message=AudioMessage)
def handle_aud(event):
    global trans, quiz, listen, stt, grade
    if(stt == True):
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
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=t))
        os.remove(path)
        text = r.recognize_google(audio,language='zh-CN')
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你的訊息是=\n'+text))
#-----------------語音處理訊息結束----------------

#出題小老師  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    global trans, quiz, listen, stt
    if(quiz == True):
        print("---Feedback---")
        global isAsked, index, sheetQA, qNumQA, star_numQA, score, qa_score

        if(isChangingLevel==True):
            levelinput = event.postback.data
            myResult = setLevelQA(levelinput) 
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
        
        elif(isChangingType == True):
            typeinput = event.postback.data
            typeResult = setTypeQA(typeinput) 
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = typeResult))
        
        else:    
            print("correct answer = ",str(sheetQA["answer"][index]))
            print("index = ", index)
            answer = event.postback.data
            if answer != str(sheetQA["answer"][index]):
                feedback = sheetQA["feedback"][index]
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
                isAsked = False       
            else:
                print('恭喜你答對了!給你一個小星星!')
                star_numQA += 1
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '恭喜你答對了!給你一個小星星!'))
                qa_score += 1
                score += 1
                print('score: ', score)
                print('qa_score: ', qa_score)
                user_sheet.update_cell(score_row, 2, score)
                user_sheet.update_cell(score_row, 3, qa_score)
                print('save!!!!!!!!!!')
                isAsked = False

            if index < qNumQA - 1:
                index += 1
            else:
                index = 0
            print("index after = ", index)
#------------------聽力回饋判斷-------------------
    elif(listen == True):
        print("---Feedback---")
        global isAsked_L
        global index_L
        global sheet,subindex
        global qNum
        global star_num
        global data_img, data_tail, data_word, data_sen, lis_score
        if(isChangingLevel_L==True):
            levelinput = event.postback.data
            myResult = setLevel(levelinput) 
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = myResult))
        else:    
            print("correct answer = ",str(sheet["answer"][subindex]))
            print("answer index_L = ", index_L)
            print("answer subindex = ", subindex)
            answer = event.postback.data
            if answer != str(sheet["answer"][subindex]):
                if(index_L >= qNum - 1): #做完本輪題庫數目
                    print('恭喜你做完這次的聽力練習了!')
                    end_feedbck =("恭喜你做完這次的聽力練習了!\n你獲得的星星是"+ str(star_num) +"顆哦!!你好棒!")
                    lis_score = lis_score + star_num
                    score = score + star_num
                    user_sheet.update_cell(score_row, 2, score)
                    user_sheet.update_cell(score_row, 4, lis_score)
                    print('score: ', score)
                    print('lis_score: ', qa_score)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = end_feedbck))
                else:
                    feedback = sheet["feedback"][subindex]
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
                    isAsked_L = False       
            else:
                star_num += 1
                if(index_L >= qNum - 1):#做完本輪題庫數目
                    print('恭喜你做完這次的聽力練習了!')
                    end_feedbck =("恭喜你做完這次的聽力練習了!\n你獲得的星星是"+ str(star_num) +"顆哦!!你好棒!")
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = end_feedbck))
                else:
                    print('恭喜你答對了!給你一個小星星!')
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '恭喜你答對了!給你一個小星星!\n'))
                    isAsked_L = False

            if index_L < qNum - 1:
                index_L += 1
            else:#做完本輪題庫數目
                index_L = 0
                star_num = 0
                #data_img, data_tail, data_word, data_sen = getSheet(level_L)
                #sheet = editSheet(data_img) 
                #print("new sheet",sheet)
            print("index_L after = ", index_L)

##出題小老師  設定Level------------------------------------------------
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
        data_Word, data_Grammar, data_Cloze = getSheetQA(level)
      
    return myResult
##出題小老師  設定出題類型------------------------------------------------
def setTypeQA(typeinput) :
    print("---Changing Level---")
    global sheetQA, qNumQA
    global isChangingType
    
    if (typeinput=='W'):
        sheetQA, qNumQA = editSheetQA(data_Word) 
        isChangingType = False
        myResult= ("題目類型切換至詞彙練習")
        
    elif (typeinput=='G'):
        sheetQA, qNumQA = editSheetQA(data_Grammar) 
        isChangingType = False
        myResult= ("題目類型切換至文法練習")    
    elif (typeinput=='C'):
        sheetQA, qNumQA = editSheetQA(data_Cloze) 
        isChangingType = False
        myResult= ("題目類型切換至克漏字練習")  
    else:       
        isChangingType = True
        myResult = "N"
    
    return myResult
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
#----------聽力function------------------
#設定Level------------------------------------------------
def setLevel(levelinput):
    print("---Changing Level---")
    global data_img, data_tail, data_word, data_sen
    global level_L
    global isChangingLevel_L
    #global pre_sheet
    if (levelinput=='L'):
        level_L = 1
        isChangingLevel_L = False
        myResult= ("目前程度切換至初級 \n 以下將開始出題")
        
    elif (levelinput=='M'):
        level_L = 2
        isChangingLevel_L = False
        myResult= ("目前程度切換至中級\n 以下將開始出題")    
    elif (levelinput=='H'):
        level_L = 3
        isChangingLevel_L = False
        myResult= ("目前程度切換至高級\n 以下將開始出題")  
    else:       
        isChangingLevel_L = True
        myResult = "N"
    
    if isChangingLevel_L == False:
        data_img, data_tail, data_word, data_sen = getSheet(level_L)
        #sheet = editSheet(pre_sheet)
        #print("level_L get sheet",sheet)
      
    return myResult

def levelButton(event):
    buttons_template = TemplateSendMessage (
                    alt_text = 'Buttons Template',
                    template = ButtonsTemplate (
                        title = '請選擇出題小老師題目程度～',
                        actions = [
                                PostbackTemplateAction(
                                    label = "初級", 
                                    text = "初",
                                    data = 'L'
                                ),
                                PostbackTemplateAction(
                                    label = "中級",
                                    text = "中",
                                    data = 'M'
                                ),
                                PostbackTemplateAction(
                                    label = "高級",
                                    text = "高",
                                    data = 'H'
                                )
                        ]
                    )
                )
    line_bot_api.reply_message(event.reply_token, buttons_template)  


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
