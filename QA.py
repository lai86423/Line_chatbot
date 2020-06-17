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

def QA_img():
    QA_img = CarouselContainer (
                        contents = [
                            BubbleContainer (
                                direction='ltr',
                                header = BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        TextComponent(text='題目(1/20)', weight='bold', size='lg', align = 'center')                   
                                    ]
                                ),
                                body = BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        ButtonComponent(
                                            action = URIAction(label = '聽題目', uri = 'https://linecorp.com'),
                                            color = '#3B9A9C',
                                            margin = 'lg',
                                            style = 'primary'
                                        ),
                                        TextComponent(text='選出聽到的答案', size='md', align = 'center'),
                                        SeparatorComponent(margin = 'xxl', color = '#A89F9F'),
                                        ButtonComponent(
                                            action = PostbackAction(label = '前往下一題', data = 'NextQ', text = '前往下一題'),
                                            color = '#F29C2B',
                                            margin = 'xxl',
                                            style = 'primary'
                                        )
                                    ]
                                )
                            ),
                            BubbleContainer (
                                direction='ltr',
                                header = BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        TextComponent(text='選項(1)', size='xl', align = 'center')
                                    ]
                                ),
                                hero = ImageComponent(
                                    url='https://sw.cool3c.com/article/2018/69de900a-b708-4a5d-8048-c1c89b6819e2.jpg?lossless=1&fm=webp&fit=max&w=1200&h=1200',
                                    size='full',
                                    aspect_ratio= '1.51:1',
                                    aspect_mode='fit'
                                ),
                                footer = BoxComponent(
                                    layout='horizontal',
                                    contents=[
                                        ButtonComponent(
                                            action = PostbackAction(label = '選項(1)', data = '1', text = '選項(1)'),
                                            color = '#46549B',
                                            style = 'primary'
                                        )
                                    ]
                                )
                            ),
                            BubbleContainer (
                                direction='ltr',
                                header = BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        TextComponent(text='選項(2)', size='xl', align = 'center')
                                    ]
                                ),
                                hero = ImageComponent(
                                    url='https://www.planetorganic.com/images/products/large/1874.jpg',
                                    size='full',
                                    aspect_ratio= '1.51:1',
                                    aspect_mode='fit'
                                ),
                                footer = BoxComponent(
                                    layout='horizontal',
                                    contents=[
                                        ButtonComponent(
                                            action = PostbackAction(label = '選項(2)', data = '2', text = '選項(2)'),
                                            color = '#7E318E',
                                            style = 'primary'
                                        )
                                    ]
                                )
                            ),
                            BubbleContainer (
                                direction='ltr',
                                header = BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        TextComponent(text='選項(3)', size='xl', align = 'center')
                                    ]
                                ),
                                hero = ImageComponent(
                                    url='https://s3.amazonaws.com/finecooking.s3.tauntonclud.com/app/uploads/2017/04/24172040/ING-grapes-2.jpg',
                                    size='full',
                                    aspect_ratio= '1.51:1',
                                    aspect_mode='fit'
                                ),
                                footer = BoxComponent(
                                    layout='horizontal',
                                    contents=[
                                        ButtonComponent(
                                            action = PostbackAction(label = '選項(3)', data = '3', text = '選項(3)'),
                                            color = '#CD2774',
                                            style = 'primary'
                                        )
                                    ]
                                )
                            )
                        ]                    
                    )
    return QA_img   

    def QA_tail():
        QA_tail = BubbleContainer (
            direction='ltr',
            header = BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='題目(1/20)', weight='bold', size='lg', align = 'center')                   
                ]
            ),
            body = BoxComponent(
                layout='vertical',
                contents=[
                    ButtonComponent(
                        action = URIAction(label = '聽題目', uri = 'https://linecorp.com'),
                        color = '#3B9A9C',
                        margin = 'lg',
                        style = 'primary',
                        flex = 10
                    ),
                    TextComponent(text='選出所聽到的單字的字尾音', size='md', align = 'center'),
                    SeparatorComponent(margin = 'xxl', color = '#A89F9F'),
                    ButtonComponent(
                        action = PostbackAction(label = '前往下一題', data = 'NextQ', text = '前往下一題'),
                        color = '#F29C2B',
                        margin = 'xxl',
                        style = 'primary'
                    ),
                    SeparatorComponent(margin='xl',color='#A89F9F'),
                    ButtonComponent(
                        action = PostbackAction(label = '(1) f', data = '1', text = '(1) f'),
                        color = '#46549B',
                        margin = 'md',
                        style = 'primary'
                    ),
                     ButtonComponent(
                        action = PostbackAction(label = '(2) b', data = '2', text = '(2) b'),
                        color = '#7E318E',
                        margin = 'md',
                        style = 'primary'
                    ),
                     ButtonComponent(
                        action = PostbackAction(label = '(3) m', data = '3', text = '(3) m'),
                        color = '#CD2774',
                        margin = 'md',
                        style = 'primary',
                        gravity='top'
                    )
                ]
            )
        )
                                           
                        
        return QA_tail

    def QA_Word():


        return QA_Word
    def QA_Sentence():


        return QA_Sentence

