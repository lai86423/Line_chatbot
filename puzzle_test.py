import numpy as np
import pandas as pd
import pygsheets
import random

GDriveJSON = 'JSON.json'
GSpreadSheet_P = 'cilab_ChatBot_puzzle'
gc_Q= pygsheets.authorize(service_account_file='JSON.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1nVIgWGQJRIQtMtZSv1HxyDb5FvthBNc0duN4Rlra8to/edit#gid=1732714016'
sh_P = gc_Q.open(GSpreadSheet_P)
sh_P.worksheet_by_title('d0').export(filename='d0')
sh_P.worksheet_by_title('r0').export(filename='r0')
sheet_d0 = pd.read_csv('d0.csv') #type: <class 'pandas.core.frame.DataFrame'>
sheet_r0 = pd.read_csv('r0.csv') 
#print(sheet_d0,sheet_r0)

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

##----------------------------------------------------------------------------------
sheet_type = 'text'
sheet_title = ''
sheet_text = ''
sheet_reply_list = []
level_P = 1
index_P = 0 #第幾題
levelsheet_d, levelsheet_r = getSheet_P(level_P)
##----------------------------------------------------------------------------------

def editSheet(data):
    #pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    print("header",data.columns)
    header = data.columns
    sheet_P = {}
    for i in range (len(header)):
        sheet_P[header[i]] = data[header[i]]
    return sheet_P

def smallpuzzle(id, sheet):
    print("-------------------")
    global sheet_type 
    global sheet_title
    global sheet_text
    global sheet_reply_list
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
            smallpuzzle(next_id , sheet)

        elif sheet_type == 'text':
            sheet_text = sheet["text"][id_index]
            print("text= ",sheet_text)
            smallpuzzle(next_id , sheet)

        elif sheet_type == 'button': 
            sheet_title = sheet["title"][id_index]
            for i in range (3):
                if (str(sheet.iloc[id_index][4 + i]) != "") : 
                    sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))

            ButtonPuzzle(sheet, sheet_reply_list, sheet_title)

        elif sheet_type == 'confirm':
            CofirmPuzzle(sheet,next_id)


    except:
        if next_id == 'd00209': #選題目階級
            Postback('L')
        #elif index == 'd10029': 
        else:
            pass

def ButtonPuzzle(sheet, reply, title):
    replylist = []
    print("ButtonPuzzle",reply)
    for i in range(len(reply)):
        id_index = sheet_r0["a-replyID"].index[sheet_r0["a-replyID"] == reply[i]]
        replylist.append(([sheet_r0["label"][id_index[0]], sheet_r0["text"][id_index[0]], sheet_r0["data"][id_index[0]]]))
    print("replylist",replylist)  
    #Button Bubble 
    #

    #smallpuzzle(id + 1 , sheet)

def CofirmPuzzle(sheet,next_id):
    print("CofirmBubble")
    smallpuzzle(next_id , sheet)

def Postback(pb_event):
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

def setLevelStory(pb_event):
    global level_P, levelsheet_d, levelsheet_r
    print("setLevelStory")
    if pb_event == 'L':
        level_P = 1
        levelsheet_d, levelsheet_r = getSheet_P(level_P)
        smallpuzzle('d10000' , levelsheet_d)
        LoadQuestion()

    elif pb_event == 'M':
        level_P = 2
        levelsheet_d, levelsheet_r = getSheet_P(level_P)
        smallpuzzle('d20000' , levelsheet_d)
        LoadQuestion()

    elif pb_event == 'H':
        level_P = 3
        levelsheet_d, levelsheet_r = getSheet_P(level_P)
        smallpuzzle('d30000' , levelsheet_d)
        LoadQuestion()
    

def RandomTest():
    global test_type_list
    test_type_list = [random.randint(0,7) for _ in range(10)]
    print(test_type_list)

def LoadQuestion():
    print("LoadQuestion",index_P)
    # if test_type_list[index_P] == 0:
    #     print("sheet_pho")
    #     smallpuzzle('d00202',levelsheet)
    # elif test_type_list[index_P] == 1:
    #     #sheet_word
    # elif test_type_list[index_P] == 2:
    #     #sheet_sen
    # elif test_type_list[index_P] == 3:
    #     #sheet_spexking_word
    # elif test_type_list[index_P] == 4:
    #     #sheet_spexking_sen
    # elif test_type_list[index_P] == 5:
    #     #sheet_voc
    # elif test_type_list[index_P] == 6:
    #     #sheet_cloze
    # elif test_type_list[index_P] == 7:
        #shhet_reading

if __name__ == "__main__":
    #sheet_d, sheet_r = getSheet_P(1)

    smallpuzzle('d00207',sheet_d0)
    # if(isAsk_P):
    #     smallpuzzle('d00000',sheet_d0)
    #RandomTest()

    #sheet_P = editSheet(sheet_d)

