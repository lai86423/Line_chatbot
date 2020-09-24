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
import QA_Bubble
import random

import getVoc
import QA_Bubble

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
GSpreadSheet_P = 'cilab_ChatBot_puzzle-1'
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
        sh_P.worksheet_by_title('d3').export(filename='d3')
        sh_P.worksheet_by_title('r3').export(filename='r3')
        sheet_d = pd.read_csv('d3.csv')        
        sheet_r = pd.read_csv('r3.csv') 
    elif(level == 2):
        sh_P.worksheet_by_title('d2').export(filename='d2')
        sh_P.worksheet_by_title('r2').export(filename='r2')
        sheet_d = pd.read_csv('d2.csv')
        sheet_r = pd.read_csv('r2.csv')

    else:        
        sh_P.worksheet_by_title('d1').export(filename='d1')
        sh_P.worksheet_by_title('r1').export(filename='r1')
        sheet_d = pd.read_csv('d1.csv')        
        sheet_r = pd.read_csv('r1.csv') 

    return sheet_d, sheet_r

##----------------------------------------------------------------------------------
# sheet_type = 'text'
# sheet_reply_list = []
# user.next_id = 0
# user.level_P = 1
# user.index_P = 0 #第幾題
# user.isInit_P = True
# user.isChangingLevel_P = False
# user.isChooseHelp = False
# user.isLoad_P = False
# user.isAsk_P = False
# user.levelsheet_d = sheet_d0
# user.levelsheet_r = sheet_r0
# _id = 0
# user.text_sheet = user.levelsheet_d
# user.test_type_list = []

##----------------------------------------------------------------------------------
class userVar():
    def __init__(self,_id):
        self._id = _id
        #QA
        self.data_Voc, self.data_Reading, self.data_Cloze = getSheetQA(1) #預設傳level = 1
        self.sheet_Q = getVoc.editSheet(self.data_Voc)
        self.isVoc = False 
        self.VocQA = []
        # #Listen
        # self.data_pho, self.data_word, self.data_sen = getSheet(self.level_L)
        # self.sheet_L = self.data_pho
        # self.isWord = False 
        # self.word_list = []

        #Puzzle
        self.next_id = 0
        self.level_P = 1
        self.index_P = 0 #第幾題
        self.isInit_P = True
        self.isChangingLevel_P = False
        self.isChooseHelp = False
        self.isLoad_P = True
        self.isPreStory_P = False
        self.isStart_P = False
        self.isAsk_P = False
        self.levelsheet_d = sheet_d0
        self.levelsheet_r = sheet_r0
        self.text_sheet = self.levelsheet_d
        self.test_type_list = []
        self.subindex_P = 0

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
    #global user.isInit_P,  user.isAsk_P, user.isLoad_P
    user = getUser(event.source.user_id)
    #---------------------------------------    
    if(user.isInit_P == True or event.message.text =='?'):
        #smallpuzzle(event,'d00000',sheet_d0, user)

        #------Test
        user.levelsheet_d, user.levelsheet_r = getSheet_P(user.level_P)
        smallpuzzle(event,'d10029',user.levelsheet_d, user)
        #------Test

        #user.isChangingLevel_P = True
        user.isInit_P = False
    # if user.isChangingLevel_P == True:
    #     user.isAsk_P = False
        
    # if(user.isStart_P == True):
    #     #if(user.isAsk_P == False):
    #     print("load_Q")
    #     #user.isAsk_P = True
    #     bubble = Question_P(event, user)
    #     message = FlexSendMessage(alt_text="bubble", contents = bubble)
    #     line_bot_api.reply_message(event.reply_token, message)

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
    #global user.isChooseHelp, user.level_P, user.isChangingLevel_P,_id, user.isLoad_P
    user = getUser(event.source.user_id)
    pb_event = event.postback.data
    print("postbackData = ",pb_event )
    if user.next_id == 'd10029' or user.next_id == 'd20025' or user.next_id == 'd30022':
        user.isLoad_P = True
    
    if (pb_event == 'Next'):
        if  user.next_id =='d00101': #重複詢問可以幫您什麼？
            smallpuzzle(event,'d00003',sheet_d0, user)
        
        elif user.next_id =='d00208':
            print("level = ",user.level_P)
            #global user.levelsheet_d, user.levelsheet_r
            user.levelsheet_d, user.levelsheet_r = getSheet_P(user.level_P)
            setLevelStory(user.level_P, user)
        
        elif user.isLoad_P == True:
            print("d100**")
            RandomTest(user)
            message = LoadTestIndex(user)
            line_bot_api.reply_message(event.reply_token, message)  
            user.isLoad_P = False
            user.isPreStory_P = True

        elif user.isPreStory_P == True:
            if user.isAsk_P == False :
                print("題前故事")
                user.isAsk_P = True
                #題前故事
                test_type = user.test_type_list[user.index_P]
                print("test_type = ", test_type)
                print('--TestPreStory--'+'d'+ str(user.level_P) + str(test_type) + '000')
                smallpuzzle(event, 'd' + str(user.level_P) + str(test_type) + '000', user.levelsheet_d, user)
            else:
                smallpuzzle(event, user.next_id , user.text_sheet, user)

        elif(user.isStart_P == True):
            print("load_Q")
            bubble = Question_P(event, user)
            message = FlexSendMessage(alt_text="bubble", contents = bubble)
            line_bot_api.reply_message(event.reply_token, message)

        else:
            smallpuzzle(event, user.next_id , user.text_sheet, user)
    
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
    elif user.isLoad_P == True:
        # if user.isWord == True:
        #         correctAns = str(user.word_list[user.subindex_L][2])

        # else:
        #     correctAns = str(user.sheet_L[user.subindex_L][4])
        # print("correct answer = ",correctAns)
        # print("answer user.index_L = ", user.index_L)
        # print("answer subuser.index_L = ", user.subindex_L)
        print("Ans feedback")

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

    # if user.isChangingLevel_P == False:
    #     print("level = ",user.level_P)
    #     global user.levelsheet_d, user.levelsheet_r
    #     user.levelsheet_d, user.levelsheet_r = getSheet_P(user.level_P)
    

def smallpuzzle(event,id, sheet, user):
    #global user.isChangingLevel_P, user.isChooseHelp, user.next_id, user.text_sheet
    print("---------id----------",id)
    # id_three = id[3]
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
            #message = ImageBubble(sheet_text)
            #line_bot_api.reply_message(event.reply_token, message)                  
            smallpuzzle(event, user.next_id , sheet, user)

        elif sheet_type == 'text':
            user.text_sheet = sheet
            sheet_text = sheet["text"][id_index]
            print("text= ",sheet_text)
            message = TextBubble(sheet_text)
            #message = TextSendMessage(text=sheet_text)
            line_bot_api.reply_message(event.reply_token, message)  
            #line_bot_api.push_message(_id, message)
            #smallpuzzle(event, user.next_id , sheet, user)

        elif sheet_type == 'button': 
            if id == 'd00003':
                user.isChooseHelp = True
            elif id == 'd00201':
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
            #line_bot_api.push_message(_id, button_bubble)  
            #Postback(str(button_bubble))
        
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
            #smallpuzzle(event, user.next_id , sheet, user)

    else:
        if user.isPreStory_P == True:
            print("PreStory End! Strat Testing!")
            user.isStart_P = True
            user.isAsk_P = False
            user.isPreStory_P = False

        print("Do Not Find ID in Sheet! ")
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
    user.test_type_list = [random.randint(1,1) for _ in range(10)]
    print("-----*** 10 Quiz type = ",user.test_type_list)

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
        #line_bot_api.push_message(_id, message)

    elif user.level_P == 3:
        test_pretext = "（第" + str(user.index_P+1) + " 題）\n【Cynthia】：\n真是太好了！剛好每天晚上Helena都會在他的閣樓唱歌給大家聽，我們趕緊去找，18:00拿去給領主吧！\n勇者，Let's go！"
        print(test_pretext)
        message = TextBubble(test_pretext)
    return message

def Question_P(event, user):
    if user.test_type_list[user.index_P] == 1:
        print("sheet_L_pho & voc")
        smallpuzzle(event,'d'+ str(user.level_P) +'1000',user.levelsheet_d, user)
        print("題目")
        user.testsheet_P = user.data_Cloze
        user.subindex_P = random.randrange(1,len(np.transpose([user.sheet_Q])[0]))
        print("data_Cloze subindex_P", user.subindex_P)
        if (user.level_P != 3):
            bubble = QA_Bubble.Cloze(user.testsheet_P, user.index_P, user.subindex_P)
        else:
            bubble = QA_Bubble.Cloze_L3(user.testsheet_P, user.index_P, user.subindex_P)

    elif user.test_type_list[user.index_P] == 2:
        print("sheet_L_sen")
        smallpuzzle(event,'d'+ str(user.level_P) +'2000',user.levelsheet_d, user)
        print("題目")

    elif user.test_type_list[user.index_P] == 3:
        print("sheet_speaking_word")
        smallpuzzle(event,'d'+ str(user.level_P) +'3000',user.levelsheet_d, user)
        print("題目")

    elif user.test_type_list[user.index_P] == 4:
        print("sheet_speaking_sen")
        smallpuzzle(event,'d'+ str(user.level_P) +'4000',user.levelsheet_d, user)
        print("題目")

    elif user.test_type_list[user.index_P] == 5:
        print("sheet_Q_voc")
        smallpuzzle(event,'d'+ str(user.level_P) +'5000',user.levelsheet_d, user)
        print("題目")

    elif user.test_type_list[user.index_P] == 6:
        print("sheet_Q_cloze")
        smallpuzzle(event,'d'+ str(user.level_P) +'6000',user.levelsheet_d, user)
        print("題目")

    elif user.test_type_list[user.index_P] == 7:
        print("sheet_Q_reading")
        smallpuzzle(event,'d'+ str(user.level_P) +'7000',user.levelsheet_d, user)
        print("題目")
    
    return bubble



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


##  End------------------------------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)