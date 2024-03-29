import numpy as np
import pandas as pd
import pygsheets
import random

GDriveJSON = 'question.json'
GSpreadSheet_Q = 'Chatbot Voc1200'
gc_Q = pygsheets.authorize(service_account_file='question.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1G5gy7173hk3kcp8AFGM8EOUvb7Wa-KmU4V0dHJQQYEk/edit#gid=831684372'
sh_P = gc_Q.open_by_url(survey_url_P)

def getPresheet(level):
    if level == 1:
        sh_P.worksheet_by_title('L1(628)').export(filename='L1')
        presheet = pd.read_csv('L1.csv') #type: <class 'pandas.core.frame.DataFrame'>
    
    elif level == 2:
        sh_P.worksheet_by_title('L2(238)').export(filename='L2')
        presheet = pd.read_csv('L2.csv') #type: <class 'pandas.core.frame.DataFrame'>
    else:
        sh_P.worksheet_by_title('L3(628)').export(filename='L3')
        presheet = pd.read_csv('L3.csv') #type: <class 'pandas.core.frame.DataFrame'>

    print("header",presheet.columns)
    header = presheet.columns
    sheet = {}
    for i in range (len(header)):
        sheet[header[i]] = presheet[header[i]]

    return sheet

def getOption(sheet, q_index):
    #for i in range (3):
    q_chinese = sheet["chinese"][q_index]
    q_english = sheet["english"][q_index]
    
    q_prefix = sheet["prefix"][q_index]
    q_part = sheet["part"][q_index]
    q_part2 = sheet["part2"][q_index]
    print("###",q_chinese,q_english,q_prefix,q_part,q_part2)

    #get same title voc index 
    same_prefix_index = sheet["prefix"].index[sheet["prefix"] == q_prefix]

    #get same part of speech voc index 
    same_part_index = sheet["part"].index[sheet["part"] == q_part]
    same_part_index2 = sheet["part2"].index[sheet["part2"] == q_part]

    #get same title and part of speech voc index
    same_index = set(same_prefix_index) & set(same_part_index)
    same_index_1 = set(same_prefix_index) & set(same_part_index2)
    same_index = same_index.union(same_index_1)

    if str(q_part2)!='nan':
        same_part2_index = sheet["part"].index[sheet["part"] == q_part2]
        same_part2_index2 = sheet["part2"].index[sheet["part2"] == q_part2]

        same_index2 = set(same_prefix_index) & set(same_part2_index)
        same_index3 = set(same_prefix_index) & set(same_part2_index2)
        same_index = same_index.union(same_index2.union(same_index3))

    #get two voc from same_index
    same_index.remove(q_index) 
    if len(same_index) >= 2 :
        option_index = random.sample(same_index, 2) 
        option_english = sheet["english"][option_index[0]]
        option_english2 = sheet["english"][option_index[1]]
    else:
        option_english = sheet["english"][same_prefix_index[0]]
        option_english2 = sheet["english"][same_prefix_index[1]]
    #print(option_english,option_english2) 
    return option_english,option_english2

def getVoc(sheet):
    q_num = len(sheet["chinese"])
    q_index = random.randint(0, q_num-2)
    q_chinese = sheet["chinese"][q_index]
    q_english = sheet["english"][q_index]
    return q_index, q_chinese, q_english

def getQA(q_english, option_english,option_english2):
    option = [q_english, option_english,option_english2]
    random.shuffle(option)
    answer = option.index(q_english)
    return option, answer

def editSheet(sheet):
    for i in range (3):
       q_index, q_chinese, q_english = getVoc(sheet)
       option_english,option_english2 = getOption(sheet, q_index)
       print(q_chinese, q_english, option_english,option_english2)
       option, answer = getQA(q_english, option_english,option_english2)
       print(option, answer)

if __name__ == "__main__":
    presheet = getPresheet(1)
    sheet = editSheet(presheet)
    
    