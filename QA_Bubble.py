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
import random

def Voc(index, sheet):
    q_chinese = sheet[0]
    option = sheet[1]
    print("q_chinese = ",q_chinese)
    print("option1 = ",option[0])
    print("option2 = ",option[1])
    print("option3 = ",option[2])
    
    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="題目("+ str(index+1) +"/10)", weight='bold', size='lg', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = q_chinese, size='xl', align = 'center',weight = 'bold'),
                TextComponent(text = "選出上方意思的單字", margin='sm', size='md', align = 'center',color = '#9F9F9F'),
                SeparatorComponent(margin = 'xl', color = '#A89F9F'),
                ButtonComponent(
                    action = PostbackAction(label = "(1) " + option[0], data = '1', text = "(1) " + option[0]),
                    color = '#46549B',
                    margin = 'xl',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(2) " + option[1], data = '2', text = "(2) " + option[1]),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(3) " + option[2], data = '3', text = "(3) " + option[2]),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )
    return Bubble   

def Cloze(sheet,index_L,subindex):
    question = sheet[subindex][0]
    option1 = sheet[subindex][1]
    option2 = sheet[subindex][2]
    option3 = sheet[subindex][3]
    print("Question = ",question) 
    print("option1 = ",option1)
    print("option2 = ",option2)
    print("option3 = ",option3) 

    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="題目("+ str(index_L+1) +"/10)", weight='bold', size='lg', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = question, size='lg', align = 'center',wrap= True),
                TextComponent(text = "選出空格中合適的答案", margin='sm', size='md', align = 'center',color = '#9F9F9F'),
                SeparatorComponent(margin = 'xl', color = '#A89F9F'),
                ButtonComponent(
                    action = PostbackAction(label = "(1) " + option1, data = '1', text = "(1) " + option1, wrap=True),
                    color = '#46549B',
                    margin = 'xl',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(2) " + option2, data = '2', text = "(2) " + option2, wrap=True),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(3) " + option3, data = '3', text = "(3) " + option3, wrap=True),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )                    
    return Bubble   

def Cloze_L3(sheet,index_L,subindex):
    question = sheet[subindex][0]
    option1 = sheet[subindex][1]
    option2 = sheet[subindex][2]
    option3 = sheet[subindex][3]
    option4 = sheet[subindex][5]
    print("Question = ",question) 
    print("option1 = ",option1)
    print("option2 = ",option2)
    print("option3 = ",option3) 
    print("option4 = ",option4)

    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="題目("+ str(index_L+1) +"/10)", weight='bold', size='lg', align = 'center')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = question, size='lg', align = 'center',wrap= True),
                TextComponent(text = "選出空格中合適的答案", margin='sm', size='md', align = 'center',color = '#9F9F9F'),
                SeparatorComponent(margin = 'xl', color = '#A89F9F'),
                ButtonComponent(
                    action = PostbackAction(label = "(1) " + option1, data = '1', text = "(1) " , wrap=True),
                    color = '#46549B',
                    margin = 'xl',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(2) " + option2, data = '2', text = "(2) " , wrap=True),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(3) " + option3, data = '3', text = "(3) ", wrap=True),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(4) " + option4, data = '4', text = "(4) ", wrap=True),
                    color = '#FFBF00',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )                    
    return Bubble  

def Reading(sheet,index_L,subindex):
    question = sheet[subindex][0]
    option1 = sheet[subindex][1]
    option2 = sheet[subindex][2]
    option3 = sheet[subindex][3]
    print("Question = ",question) 
    print("option1 = ",option1)
    print("option2 = ",option2)
    print("option3 = ",option3) 

    Bubble = BubbleContainer (
        direction='ltr',
        header = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text="題目("+ str(index_L+1) +"/10)", weight='bold', size='lg', align = 'center',gravity='top')                   
            ]
        ),
        body = BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(text = question, size='lg',margin= 'lg',wrap= True),
                TextComponent(text = "(1) " + option1, size='lg',wrap=True),
                TextComponent(text = "(2) " + option2, size='lg',wrap=True),
                TextComponent(text = "(3) " + option3, size='lg',wrap=True),
                SeparatorComponent(),
                ButtonComponent(
                    action = PostbackAction(label = "(1) ", data = '1', text = "(1)" ),
                    color = '#46549B',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(2) ", data = '2', text = "(2)"),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(3) ", data = '3', text = "(3)"),
                    color = '#CD2774',
                    margin = 'md',
                    style = 'primary',
                    gravity='top'
                )
            ]
        )
    )                       
    return Bubble

def Article(sheet,subindex):
    try:
        article = sheet[subindex][5]
        print("article = ",article)

        Bubble = BubbleContainer (
            direction='ltr',
            header = BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text= "請閱讀底下短文", weight='bold', size='lg', gravity= 'top', align = 'start')                   
                ]
            ),
            body = BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text= article, wrap = True)
                ]
            )
        )     
        return Bubble    

    except:
        print("Article bubble except !")    

    

