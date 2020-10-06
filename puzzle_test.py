import numpy as np
import pandas as pd
import pygsheets
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

GDriveJSON = 'JSON.json'
GSpreadSheet_P = 'cilab_ChatBot_puzzle-1'
gc_Q= pygsheets.authorize(service_account_file='JSON.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1nVIgWGQJRIQtMtZSv1HxyDb5FvthBNc0duN4Rlra8to/edit#gid=1732714016'
sh_P = gc_Q.open(GSpreadSheet_P)
sh_P.worksheet_by_title('d0').export(filename='d0')
sh_P.worksheet_by_title('r0').export(filename='r0')
sheet_d0 = pd.read_csv('d0.csv') #type: <class 'pandas.core.frame.DataFrame'>
sheet_r0 = pd.read_csv('r0.csv') 
allUser = []
#---------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('JSON.json', scope)
client = gspread.authorize(creds)
spreadSheet = client.open('cilab_ChatBot_QA')
sheet_Reading = spreadSheet.worksheet("L1_Reading")
data_Reading = sheet_Reading.get_all_values()
#print("data_Reading", data_Reading[1][0])

#print(user_data["answer"][0])
#print(sheet_d0,sheet_r0)
class userVar_P():
    def __init__(self,_id):
        self._id = _id
        self.isInit_P = True
        self.isChangingLevel_P = True
        # self.sheet_type = 'text'
        # self.sheet_title = ''
        # self.sheet_text = ''
        #self.sheet_reply_list = []
        self.level_P = 1
        self.index_P = 0 #第幾題
        self.levelsheet_d, self.levelsheet_r = getSheet_P(self.level_P)

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
# sheet_type = 'text'
# level_P = 1
# index_P = 0 #第幾題
# isInit_P = True
# isChangingLevel_P = False
# isChooseHelp = False
# isStart_P = False
# isAsk_P = False
# levelsheet_d, levelsheet_r = getSheet_P(level_P)
##----------------------------------------------------------------------------------
def editSheet(data):
    #pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    print("header",data.columns)
    header = data.columns
    sheet_P = {}
    for i in range (len(header)):
        sheet_P[header[i]] = data[header[i]]
    return sheet_P

def smallpuzzle(event,id, sheet):
    global isChangingLevel_P, isChooseHelp
    print("-------------------")
    print("id",id)
    print("id-1: ",id[1:2],id[2:3])

    id_index = sheet["a-descriptionID"].index[sheet["a-descriptionID"] == id] 
    print("#####",id_index) 
    if len(id_index) > 0:
        id_index = id_index[0]
        print("id_index",id_index)

        print("id-3: ",id[1:4])
        next_id = id[0:3]+ str( int(id[3:6]) + 1).zfill(3)
        print("next id = ", next_id)

        sheet_type = sheet["type"][id_index]
        print("sheet_type",sheet_type)
        
        if sheet_type == 'image':   
            sheet_text = sheet["text"][id_index]  
            print("img= ",sheet_text)                   
            smallpuzzle(event, next_id , sheet)

        elif sheet_type == 'text':
            sheet_text = sheet["text"][id_index]
            #sheet["text"][id_index].color = (0.9529412, 0.9529412, 0.9529412, 0)
            print("text= ",sheet_text)
            smallpuzzle(event, next_id , sheet)

        elif sheet_type == 'button': 
            if id == 'd00003':
                isChooseHelp = True
            elif id == 'd00201':
                isChangingLevel_P = True
            sheet_title = sheet["title"][id_index]
            sheet_text = sheet["text"][id_index]
            sheet_reply_list = []
            for i in range (3):
                if (str(sheet.iloc[id_index][4 + i]) != "") : 
                    sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))

            replylist = ButtonPuzzle(sheet_reply_list, sheet_title)
            button_bubble = ButtonBubble(sheet_title, sheet_text, replylist)
            Postback(str(button_bubble))
        
        elif sheet_type == 'confirm':
            sheet_text = sheet["text"][id_index]
            # sheet_reply_list = []
            # for i in range (2):
            #     if (str(sheet.iloc[id_index][4 + i]) != "") : 
            #         sheet_reply_list.append((str(sheet.iloc[id_index][4 + i])))

            # replylist = CofirmPuzzle(sheet_reply_list)
            print("confirm= ",sheet_text)
            smallpuzzle(event, next_id , sheet)


    else:
        #if next_id == 'd00209': #選題目階級
        #    Postback('L')
        #elif index == 'd10029': 
        print("Do Not Find ID in Sheet! ")
        pass

def ButtonPuzzle(reply, title):
    replylist = []
    print("ButtonPuzzle",reply)
    for i in range(len(reply)):
        id_index = sheet_r0["a-replyID"].index[sheet_r0["a-replyID"] == reply[i]]
        replylist.append(([sheet_r0["label"][id_index[0]], sheet_r0["text"][id_index[0]], sheet_r0["data"][id_index[0]]]))
    #print("replylist",replylist)  
    return replylist

def CofirmPuzzle(reply):
    print("CofirmBubble",reply)
    replylist = []
    for i in range(len(reply)):
        id_index = sheet_r0["a-replyID"].index[sheet_r0["a-replyID"] == reply[i]]
        replylist.append(([sheet_r0["label"][id_index[0]], sheet_r0["text"][id_index[0]], sheet_r0["data"][id_index[0]]]))
    print("Comfirm replylist",replylist)  
    return replylist

def Postback(pb_event):
    global isChooseHelp, level_P, isChangingLevel_P
    if pb_event == 0:
        pass
    #--Game State-----------------------------------
    elif pb_event == '1':
        if isChooseHelp == True:
            isChooseHelp = False
            #了解背景故事
            smallpuzzle(event,'d00100',sheet_d0)
            #重複詢問可以幫您什麼？
            smallpuzzle(event,'d00003',sheet_d0)
    elif pb_event == '2':
        if isChooseHelp == True:
            isChooseHelp = False
            #開始遊戲
            smallpuzzle(event,'d00200',sheet_d0)

    elif pb_event == '3':
        if isChooseHelp == True:
            #結束遊戲
            print("End!")
        pass

    if isChangingLevel_P == True:
        isChangingLevel_P = False
        #隨機取得題型
        RandomTest()
        print("level = ",int(pb_event))
        level_P = int(pb_event)
        smallpuzzle(event,'d00202',sheet_d0)
        setLevelStory(pb_event)
        isChangingLevel_P = False

def setLevelStory(event):
    print("setLevelStory")
    global levelsheet_d, levelsheet_r, isStart_P
    levelsheet_d, levelsheet_r = getSheet_P(level_P)
    if level_P == 1:
        smallpuzzle(event,'d10000' , levelsheet_d)

    elif level_P == 2:
        smallpuzzle(event,'d20000' , levelsheet_d)

    elif level_P == 3:
        smallpuzzle(event,'d30000' , levelsheet_d)

    isStart_P = True
    

def RandomTest():
    global test_type_list
    test_type_list = [random.randint(1,7) for _ in range(10)]
    print(test_type_list)
    
    for i in range (len(test_type_list)):
        print("TYPE",type(test_type_list[i]))
        test_type_list[i] = str(test_type_list[i])
        print("TYPE",type(test_type_list[i]))

def LoadQuestion(event):
    print("-----LoadQuestion------", index_P)

    #題數引文
    if level_P == 1 :
        print("（第$" + str(index_P+1) + "count 題）\n【Silas】：\n勇者$username ，現在是 "+ str(8+index_P) +":00，Ariel 希望我們在傍晚18:00前完成。")
    elif level_P == 2:
        print("（第$" + str(index_P+1) + "count 題）\n【Keith】：\n勇者$username ，現在是 "+ str(8+index_P) +":00，Faun 希望我們在傍晚18:00前完成。")
    elif level_P == 3:
        print("（第$" + str(index_P+1) + "【Cynthia】：\n真是太好了！剛好每天晚上Helena都會在他的閣樓唱歌給大家聽，我們趕緊去找，18:00拿去給領主吧！\n勇者，Let's go！")
    
def Question_P(event):
    print("-----Question_P------", index_P)
    if test_type_list[index_P] == 1:
        print("sheet_pho")
        smallpuzzle(event,'d'+ str(level_P) +'1000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 2:
        print("sheet_word")
        smallpuzzle(event,'d'+ str(level_P) +'2000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 3:
        print("sheet_sen")
        smallpuzzle(event,'d'+ str(level_P) +'3000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 4:
        print("sheet_spexking_word")
        smallpuzzle(event,'d'+ str(level_P) +'4000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 5:
        print("sheet_spexking_sen")
        smallpuzzle(event,'d'+ str(level_P) +'5000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 6:
        print("sheet_cloze")
        smallpuzzle(event,'d'+ str(level_P) +'6000',levelsheet_d)
        print("題目")

    elif test_type_list[index_P] == 7:
        print("sheet_reading")
        smallpuzzle(event,'d'+ str(level_P) +'7000',levelsheet_d)
        print("題目")

def getUser(user_ID):
    global allUser
    user = next((item for item in allUser if item._id == user_ID), None)
    if user is None:
        user = userVar_P(user_ID)
        allUser.append(user)
        #print("Alluser",allUser)
    return user 

def ButtonBubble(sheet_title, sheet_text, replylist):
    print(sheet_title,sheet_text)
    for i in range(3):
        print(replylist[i][2],replylist[i][1])
    ans = input("input 1 or 2 or 3 :")
    return ans

if __name__ == "__main__":
    #sheet_d, sheet_r = getSheet_P(1)
    sheet_type = 'text'
    level_P = 1
    index_P = 0 #第幾題
    isInit_P = True
    isChangingLevel_P = False
    isChooseHelp = False
    isStart_P = False
    isAsk_P = False
    levelsheet_d, levelsheet_r = getSheet_P(level_P)
    test_type_list = []
    #global isInit_P,  isAsk_P, isStart_P
    user = getUser("12345")
    event = '123' 
    if(isInit_P == True ):
        smallpuzzle(event,'d00000',sheet_d0)
        #isChangingLevel_P = True
        isInit_P = False
    if(isStart_P == True):
        print("----???/",isAsk_P)
        if(isAsk_P == False):
            isAsk_P = True
            print("----isAsk_P!!!!!",isAsk_P)
            
            LoadQuestion(event)

            test_type = test_type_list[index_P]
            print("test_type = ", test_type)
            #題前故事
            print('d'+ str(level_P) + str(test_type) + '000')
            smallpuzzle(event, 'd' + str(level_P) + str(test_type) + '000', levelsheet_d)
            Question_P(event)
    #if(isChangingLevel_P == True):
       #smallpuzzle(event,'d00000',sheet_d0)


