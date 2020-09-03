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

def Voc(index_L, VocQA):
    # question = sheet["question"][subindex]
    # print("option1 = ",sheet["option1"][subindex])
    # print("option2 = ",sheet["option2"][subindex])
    # print("option3 = ",sheet["option3"][subindex])
    # print("Question = ",question)
    q_chinese = VocQA[0]
    option = VocQA[1]
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
                    action = PostbackAction(label = "(1) " + option1, data = '1', text = "(1) " + option1),
                    color = '#46549B',
                    margin = 'xl',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(2) " + option2, data = '2', text = "(2) " + option2),
                    color = '#7E318E',
                    margin = 'md',
                    style = 'primary'
                ),
                ButtonComponent(
                    action = PostbackAction(label = "(3) " + option3, data = '3', text = "(3) " + option3),
                    color = '#CD2774',
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
                TextComponent(text = "(1) " +sheet["option1"][subindex], size='lg',wrap=True),
                TextComponent(text = "(2) " +sheet["option2"][subindex], size='lg',wrap=True),
                TextComponent(text = "(3) " +sheet["option3"][subindex], size='lg',wrap=True),
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
        article = sheet[subindex_Q][5]
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
    except:
        print("Article bubble except !")    

    return Bubble

