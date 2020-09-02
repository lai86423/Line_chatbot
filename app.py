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
class userVar_P():
    def __init__(self,_id):
        self._id = _id
        self.isInit_P = True
        self.isChangingLevel_P = True
        # self.sheet_type = 'text'
        # self.sheet_title = ''
        # self.sheet_text = ''
        #self.sheet_reply_list = []
        self.level_P = 1
        self.index_P = 0 #第幾題
        self.levelsheet_d, self.levelsheet_r = getSheet_P(self.level_P)

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
        if(user.isInit_P == True or event.message.text =='?'):
            smallpuzzle(event,'d00000',sheet_d0)
            user.isChangingLevel_P = True
            user.isInit_P = False
        #if(user.isChangingLevel_Q == True): 
        
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
    pb_event = event.postback.data
    print("postbackData = ",pb_event )

    if pb_event == 0:
        pass
    #--Game State-----------------------------------
    elif pb_event == 1:
        smallpuzzle('d00100',sheet_d0)
    elif pb_event == 2:
        smallpuzzle('d00200',sheet_d0)
    elif pb_event == 3:
        pass
    #--Set Level-----------------------------------
    elif pb_event == 'L' or pb_event == 'M' or pb_event == 'H':
        RandomTest()
        setLevelStory(pb_event)

        
##-----------------------------------------------------------------------------------
def smallpuzzle(event, id, sheet):
    print("-------------------")
    user = getUser(event.source.user_id)
    # id_three = id[3]
    next_id = id[0:3]+ str( int(id[3:6]) + 1).zfill(3)
    print("next id = ", next_id)
    
    try:
        id_index = sheet["a-descriptionID"].index[sheet["a-descriptionID"] == id]  
        id_index = id_index[0]
        print("id_index",id_index)

        sheet_type = sheet["type"][id_index]
        print("sheet_type",sheet_type)
        
        if sheet_type == 'image':   
            sheet_text = sheet["text"][id_index]  
            print("img= ",sheet_text)               
            message = ImageSendMessage(original_content_url=sheet_text, preview_image_url=sheet_text)
            line_bot_api.push_message(user._id, message)    
            smallpuzzle(event, next_id , sheet)

        elif sheet_type == 'text':
            sheet_text = sheet["text"][id_index]
            print("text= ",sheet_text)
            message = TextSendMessage(text=sheet_text)
            line_bot_api.push_message(user._id, message)
            smallpuzzle(event, next_id , sheet)

        elif sheet_type == 'button': 
            sheet_title = sheet["title"][id_index]
            sheet_text = sheet["text"][id_index]
            print("sheet_title= ",sheet_title)
            sheet_reply_list =[]
            for i in range (3):
                if (str(sheet.iloc[id_index][4 + i]) != "") : 
                    sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))

            print("sheet_reply_list", sheet_reply_list)
            replylist = ButtonPuzzle(sheet_reply_list, sheet_title)

            button_bubble = ButtonBubble(sheet_title, sheet_text, replylist)
            line_bot_api.push_message(user._id, button_bubble)

        elif sheet_type == 'confirm':
            CofirmPuzzle(sheet,next_id)


    except:
        pass
        # if next_id == 'd00209': #選題目階級
        #     Postback('L')
        # #elif index == 'd10029': 
        # else:
        #     pass

def ButtonPuzzle(sheet_reply_list, title):
    replylist = []
    print("ButtonPuzzle",sheet_reply_list)
    for i in range(len(sheet_reply_list)):
        id_index = sheet_r0["a-replyID"].index[sheet_r0["a-replyID"] == sheet_reply_list[i]]
        replylist.append(([sheet_r0["label"][id_index[0]], sheet_r0["text"][id_index[0]], sheet_r0["data"][id_index[0]]]))
    print("replylist",replylist) 
    return replylist


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


##  End------------------------------------------------

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)