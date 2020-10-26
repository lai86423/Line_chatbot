import numpy as np
import pandas as pd
import pygsheets
import random

# GDriveJSON = 'JSON.json'
# GSpreadSheet_P = 'cilab_ChatBot_Voc1200'
# gc_P = pygsheets.authorize(service_account_file='question.json')
# survey_url_P = 'https://docs.google.com/spreadsheets/d/1G5gy7173hk3kcp8AFGM8EOUvb7Wa-KmU4V0dHJQQYEk/edit#gid=831684372'
# sh_P = gc_P.open_by_url(survey_url_P)

GDriveJSON = 'JSON.json'
GSpreadSheet_L = 'cilab_ChatBot_listening'
gc_L = pygsheets.authorize(service_account_file='JSON.json') #檔案裡的google user.sheet_L js檔
sh_L = gc_L.open(GSpreadSheet_L)
VocQA = []

def getSheet(level,sh_P):
    if level == 1:
        sh_P.worksheet_by_title('L1_Voc').export(filename='L1')
        presheet = pd.read_csv('L1.csv') #type: <class 'pandas.core.frame.DataFrame'>
    
    elif level == 2:
        sh_P.worksheet_by_title('L2_Voc').export(filename='L2')
        presheet = pd.read_csv('L2.csv') #type: <class 'pandas.core.frame.DataFrame'>
    else:
        sh_P.worksheet_by_title('L3_Voc').export(filename='L3')
        presheet = pd.read_csv('L3.csv') #type: <class 'pandas.core.frame.DataFrame'>
    return presheet

def editSheet(level_sheet):
    #print("header",level_sheet.columns)
    header = level_sheet.columns
    sheet = {}
    for i in range (len(header)):
        sheet[header[i]] = level_sheet[header[i]]

    return sheet

def getOption(sheet, q_index):
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
    same_prefix_index = set(same_prefix_index)
    same_prefix_index.remove(q_index)
    
    if len(same_index) >= 2 : #取詞性和字首都相同
        option_index = random.sample(same_index, 2) 

    elif len(same_index) == 1 : #詞性和字首都相同的選擇只有一個
        option_index = list(same_index)
        same_prefix_index.remove(option_index)
        #另一個拿隨機同字首
        option_index.append(random.sample(list(same_prefix_index), 1)[0])
        print("TYPE2 option",option_index)
    elif len(same_prefix_index) >= 2 : #取兩個隨機同字首
        option_index = random.sample(same_prefix_index, 2) 
    elif len(same_prefix_index) == 1 : #同字首只有一個
        option_index = list(same_prefix_index)
        same_part_index = set(same_part_index)
        same_part_index.remove(q_index)
        option_index.append(random.sample(list(same_part_index), 1)[0])
    else: #隨機取同詞性
        option_index = random.sample(list(same_part_index), 2) 

    option_english = sheet["english"][option_index[0]]
    option_english2 = sheet["english"][option_index[1]]

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
    answer  = option.index(q_english) + 1
    return option, answer

def getAudio(sheet, q_index):
    try:
        q_audio = sheet["audio"][q_index]
    except:
        q_audio = '0'#建議可以多做一個找不到音檔的網址
    return q_audio

if __name__ == "__main__":
    #VocQA = np.empty((3,3, dtype='str'))
    presheet = getSheet(3,sh_L)
    sheet = editSheet(presheet)
    for i in range (3):
        try:
            print(VocQA[i])
        except: 
            q_index, q_chinese, q_english = getVoc(sheet)
            option_english,option_english2 = getOption(sheet, 226)
            print(q_chinese, q_english, option_english,option_english2)
            option, answer = getQA(q_english, option_english,option_english2)
            print(option, answer)
            q_audio = getAudio(sheet, q_index)
            templist = [q_chinese, option, answer,q_audio]
            VocQA.append(templist)
