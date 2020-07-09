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
line_bot_api = LineBotApi('mIg76U+23oiAkDahsjUoK7ElbuYXzLDJcGXaEjaJIfZ+mMqOO3BvX+RlQIzx/Zu0Smy8W08i01F38xGDg6r/thlWLwGxRvcgExAucwMag8KPVAkBFfSLUvgcrxQS4HBzOGIBxoo+zRSJhOFoBEtCVQdB04t89/1O/w1cDnyilFU=')
#Channel Secret  
handler = WebhookHandler('bc9f08c9c29eccb41c7b5b8102b55fd7')
#users = np.array(('0','0',0)) #userID,level,point

##翻譯小達人  變數------------------------------------------------

isAsked = True
isChangingTrans = True
isEnded = False
TransType = 1 #(ETC= 1, CTE =2)
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
    #myId = event.source.user_id
    global isAsked, isChangingTrans, isEnded
    replytext = event.message.text
    if event.message.type == 'text':   
        if replytext =='?':
            isChangingTrans = True

        if (isChangingTrans == True):  
            isAsked = True
            isEnded = False
            buttons_template = TemplateSendMessage (
                alt_text = 'Buttons Template',
                template = ButtonsTemplate (
                    title = '翻譯小達人',
                    text = '有什麼要我幫忙翻譯的嗎?',
                    thumbnail_image_url='https://upload.cc/i1/2020/07/01/IV2yHq.png',
                    actions = [
                            PostbackTemplateAction(
                                label = "英文翻中文", 
                                text = "英文翻中文",
                                data = 'ETC'
                            ),
                            PostbackTemplateAction(
                                label = "中文翻英文",
                                text = "中文翻英文",
                                data = 'CTE'
                            )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, buttons_template)
            
        elif( isAsked == False ):  
            translatedMessage = translation(replytext)
            print("tenasM = ",translatedMessage)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text = translatedMessage))

            Translation_bubble = Choose_NextStep()
            message2 = FlexSendMessage(alt_text="Translation_bubble", contents = Translation_bubble)
            line_bot_api.reply_message(event.reply_token,message2)
            isAsked = True 
        else:
            if(isEnded == True):
                message = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"
                line_bot_api.reply_message(event.reply_token,message)
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
                                action = PostbackAction(label = '翻下一句', data = 'Next', text = '翻下一句'),
                                color = '#F1C175',
                                style = 'primary',
                                gravity = 'center',
                                margin = 'md'
                            ),
                            ButtonComponent(
                                action = PostbackAction(label = '結束翻譯', data = 'End', text = '結束翻譯'),
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
    global isAsked,TransType,isChangingTrans,isEnded
    
    if(isChangingTrans==True):
        isChangingTrans = False
        levelinput = event.postback.data
        if (levelinput=='ETC'):
            TransType = 1
            print("切換英翻中模式")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請將你想翻譯的單字或句子傳送給我哦~"))
            isAsked = False

        elif (levelinput=='CTE'):
            TransType = 2
            print("切換英翻中模式")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請將你想翻譯的單字或句子傳送給我哦~"))
            isAsked = False   
        else:       
            isChangingTrans = True
            isAsked = True
        
    if(levelinput == 'Next'):
        isAsked = False
    
    if(levelinput == 'End'):
        isEnded = True
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "謝謝你使用翻譯小達人~~\n歡迎點開下方選單，使用其他功能哦！"))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
