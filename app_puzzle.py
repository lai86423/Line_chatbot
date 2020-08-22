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

import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level_P,point

allUser = [] 
##-----------------------------------------------------------------------------------
##出題  初始抓資料＆資料處理
GDriveJSON = 'question.json'
GSpreadSheet_P = 'cilab_ChatBot_puzzle'
gc_Q= pygsheets.authorize(service_account_file='question.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1nVIgWGQJRIQtMtZSv1HxyDb5FvthBNc0duN4Rlra8to/edit#gid=1732714016'
sh_P = gc_Q.open_by_url(survey_url_P)
sh_P.worksheet_by_title('d0').export(filename='d0')
sh_P.worksheet_by_title('r0').export(filename='r0')
sheet_d0 = pd.read_csv('d0.csv') #type: <class 'pandas.core.frame.DataFrame'>
sheet_r0 = pd.read_csv('r0.csv') 
print(sheet_d0,sheet_r0)
##----------------------------------------------------------------------------------
def getSheet_P(level): 
    global sh_P  
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

def editSheet(data):
    #pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    print("header",data.columns)
    header = data.columns
    sheet_P = {}
    for i in range (len(header)):
        sheet_P[header[i]] = data[header[i]]
    return sheet_P

##TODO 個人ＩＤ變數------------------------------------------------
class userVar_P():
    def __init__(self,_id):
        self._id = _id
        self.level_P = 1 # 預設level 1
        self.qNum_P = 10 # 每輪題目數量
        self.star_num_P = 0 #集點
        self.isAsked_P = False #出題與否
        self.isChangingLevel_P = True
        self.isStart_P = False
        self.index_P = 0 #第幾題
        self.isInit_P = True
        self.subindex_P = self.index_P
        self.count_P = 1
        self.presheet_d, self.presheet_r = getSheet_P(self.level_P) #預設傳level = 1
        print("self.presheet_d,presheet_r",self.presheet_d,self.presheet_r)
        self.sheet_d = editSheet(self.presheet_d,'d') 
        self.sheet_r = editSheet(self.presheet_r,'r') 
        print("self.sheet_d",self.sheet_d)
        print("self.sheet_r",self.sheet_r)

def deterOutput(messege_id,sliceNum):
    print(messege_id[:sliceNum])
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
    # global isAsked_P,isInit_P
    # global index_P
    # global isChangingLevel_P
    # global sheet_P,subindex_P
    user = getUser(event.source.user_id)
    #---------------------------------------
    #if event.message.type == 'text':   
        
##-----------------------------------------------------------------------------------
def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar_P(user_ID)
        allUser.append(user)
        print("Alluser",allUser)
    return user 

#回饋判斷
@handler.add(PostbackEvent)
def handle_postback(event):
    user = getUser(event.source.user_id)
    print("postbackData = ",event.postback.data )

        
##-----------------------------------------------------------------------------------
#設定Level------------------------------------------------
def setLevel(levelinput,user):
    print("---Changing Level---")
    #global data_Voc, data_Reading, data_Cloze
    #global level_P
    #global isChangingLevel_P
    if (levelinput=='L'):
        user.level_P = 1
        myResult = readyBubble(user.level_P)
        user.isChangingLevel_P = False
        
    elif (levelinput=='M'):
        user.level_P = 2
        myResult = readyBubble(user.level_P)    
        user.isChangingLevel_P = False

    elif (levelinput=='H'):
        user.level_P = 3
        myResult = readyBubble(user.level_P)
        user.isChangingLevel_P = False

    else:       
        user.isChangingLevel_P = True
        myResult = "N"

    if user.isChangingLevel_P == False:
        user.data_Voc, user.data_Reading, user.data_Cloze = getSheet(user.level_P)
        
    return myResult

def Question(user):
    #global subindex_P,sheet_P
    print("選完階級開始出題")
    #print("index_P",index_P)
    #print("subindex_P = ", subindex_P)
    if user.index_P < 3:
        user.subindex_P = user.index_P
        user.sheet_P = editSheet(user.data_Voc)
        QA_bubble = QA_Bubble.Voc(user.sheet_P,user.index_P,user.subindex_P)
    elif user.index_P < 7:
        user.subindex_P = user.index_P - 3
        user.sheet_P = editSheet(user.data_Cloze)
        QA_bubble = QA_Bubble.Cloze(user.sheet_P,user.index_P,user.subindex_P)
    else:
        user.subindex_P = user.index_P - 7
        user.sheet_P = editSheet(user.data_Reading) 
        QA_bubble = QA_Bubble.Reading(user.sheet_P,user.index_P,user.subindex_P)
    return QA_bubble

##  End------------------------------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)