from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

def totalStar():
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
                TextComponent(text="恭喜你獲得了" + str(star_num) + "星星!" , size='xs', align = 'center'),
                SeparatorComponent(margin='md'),
                ButtonComponent(
                    action = PostbackAction(label = "下一大題", data = 'next', text = "下一大題"),
                    color = '#F1C175',
                    margin = 'md',
                    style = 'primary',
                ),
                ButtonComponent(
                    action = PostbackAction(label = "我不答了", data = 'end', text = "我不答了"),
                    color = '#E18876',
                    margin = 'md',
                    style = 'primary',
                )
            ]  
        )
    )  
    return Bubble 