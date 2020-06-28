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

def QA_Img(sheet,subindex):
    question = sheet["question"][subindex]
    print("option1 = ",sheet["option1"][subindex])
    print("option2 = ",sheet["option2"][subindex])
    print("option3 = ",sheet["option3"][subindex])
    print("Question = ",question)  #question 是 url 網址

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
                                            action = URIAction(label = '聽題目', uri = question),
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
                                    url=sheet["option1"][subindex],
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
                                    url=sheet["option2"][subindex],
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
                                    url=sheet["option3"][subindex],
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

def QA_Tail(sheet,subindex):
    question = sheet["question"][subindex]
    print("option1 = ",sheet["option1"][subindex])
    print("option2 = ",sheet["option2"][subindex])
    print("option3 = ",sheet["option3"][subindex])
    print("Question = ",question)  #question 是 url 網址

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
                    action = URIAction(label = '聽題目', uri = question),
                    color = '#3B9A9C',
                    margin = 'lg',
                    style = 'primary',
                    flex = 10
                ),
                TextComponent(text='選出所聽到的單字的字尾音', size='md', align = 'center'),
                SeparatorComponent(margin='xl',color='#A89F9F'),
                ButtonComponent(
                    action = PostbackAction(label = "(1) " +sheet["option1"][subindex], data = '1', text = "(1) " + sheet["option1"][subindex]),
                    color = '#46549B',
                    margin = 'md',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(2) " + sheet["option2"][subindex], data = '2', text = "(2) " + sheet["option2"][subindex]),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(3) " + sheet["option3"][subindex], data = '3', text = "(3) " + sheet["option3"][subindex]),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )              
    return QA_tail

def QA_Word(sheet,subindex):
    question = sheet["question"][subindex]
    print("option1 = ",sheet["option1"][subindex])
    print("option2 = ",sheet["option2"][subindex])
    print("option3 = ",sheet["option3"][subindex])
    print("Question = ",question)  #question 是 url 網址

    QA_word = BubbleContainer (
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
                    action = URIAction(label = '聽題目', uri = question),
                    color = '#3B9A9C',
                    margin = 'lg',
                    style = 'primary',
                    flex = 10
                ),
                TextComponent(text='選出所聽到的單字', size='md', align = 'center'),
                SeparatorComponent(margin='xl',color='#A89F9F'),
                ButtonComponent(
                    action = PostbackAction(label = "(1) " +sheet["option1"][subindex], data = '1', text = "(1) " +sheet["option1"][subindex]),
                    color = '#46549B',
                    margin = 'md',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(2) " +sheet["option2"][subindex], data = '2', text = "(2) " +sheet["option2"][subindex]),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(3) " +sheet["option3"][subindex], data = '3', text = "(3) " +sheet["option3"][subindex]),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )                       
    return QA_word

def QA_Sentence(sheet,subindex):
    QA_sentence = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text='題目(16/20)', weight='bold', size='lg', align = 'center')                   
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
                TextComponent(text='選出正確的應對句子', size='md', align = 'center'),
                SeparatorComponent(margin='xl',color='#A89F9F'),
                TextComponent(text="(1) " +sheet["option1"][subindex], size='lg',margin='sm', align = 'start'),
                TextComponent(text="(2) " +sheet["option2"][subindex], size='lg',margin='sm', align = 'start'),
                TextComponent(text="(3) " +sheet["option3"][subindex], size='lg',margin='sm', align = 'start'),

                ButtonComponent(
                    action = PostbackAction(label = "(1) " +sheet["option1"][subindex], data = '1', text = "(1) " +sheet["option1"][subindex]),
                    color = '#46549B',
                    margin = 'xl',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(2) " +sheet["option2"][subindex], data = '2', text = "(2) " +sheet["option2"][subindex]),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                    ButtonComponent(
                    action = PostbackAction(label = "(3) " +sheet["option3"][subindex], data = '3', text = "(3) " +sheet["option3"][subindex]),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )                       
    return QA_sentence

