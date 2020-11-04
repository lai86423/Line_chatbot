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

##翻譯小達人  import-----------------------------------------------
import sys
import datetime
import pygsheets

app = Flask(__name__)

#Channel Access Token
line_bot_api = LineBotApi('請填LineBotApi')
#Channel Secret  
handler = WebhookHandler('請填WebhookHandler')

allUser = []
#個人ＩＤ變數------------------------------------------------
class userVar_T():
    def __init__(self,_id):
        self._id = _id
        self.isAsked = True
        self.isChangingTrans = True
        self.isEnded = False
        self.TransType = 1 #(ETC= 1, CTE =2)
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

##翻譯小達人  處理訊息------------------------------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
    user = getUser(event.source.user_id)
    myId = event.source.user_id
    #global isAsked, user.isChangingTrans, user.isEnded
    replytext = event.message.text
    if event.message.type == 'text':   
        if replytext =='?':
            user.isChangingTrans = True
            user.isEnded = False

        if (user.isChangingTrans == True ):  
            user.isAsked = True
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
            
        elif( user.isAsked == False ):  
            translatedMessage = translation(replytext, user)
            print("tenasM = ",translatedMessage)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = translatedMessage))

            Translation_bubble = Choose_NextStep()
            message2 = FlexSendMessage(alt_text="Translation_bubble", contents = Translation_bubble)
            line_bot_api.push_message(myId, message2)
            user.isAsked = True 
        else:
            if(user.isEnded == True):
                #isAsked = True
                message = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"
                #line_bot_api.reply_message(event.reply_token,message)
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

#翻譯小達人  回饋判斷------------------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    print("---Feedback---")
    user = getUser(event.source.user_id)
    levelinput = event.postback.data
    if(user.isChangingTrans==True):
        user.isChangingTrans = False
        if (levelinput=='ETC'):
            user.TransType = 1
            print("切換英翻中模式")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "目前切換 英文翻中文模式！\n請將你想翻譯的英文單字或句子傳送給我哦~"))
            user.isAsked = False

        elif (levelinput=='CTE'):
            user.TransType = 2
            print("切換中翻英模式")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "目前切換 中文翻英文模式！\n請將你想翻譯的中文字詞或句子傳送給我哦~"))
            user.isAsked = False   
        else:       
            user.isChangingTrans = True
            user.isAsked = True
        
    if(levelinput == 'Next'):
        if(user.isEnded == False):
            if(user.TransType == 1):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請傳送英文單字或句子~"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請傳送中文字詞或句子~"))
      
            user.isAsked = False
    
    if(levelinput == 'End'):
        user.isEnded = True
        user.isAsked = True  
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"))
##-----------------------------------------------------------------------------------
def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar_T(user_ID)
        allUser.append(user)
        print("Alluser",allUser)
    return user 

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
