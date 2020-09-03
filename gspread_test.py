import numpy as np
import pandas as pd
import pygsheets
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#---------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('JSON.json', scope)
client = gspread.authorize(creds)
spreadSheet = client.open('cilab_ChatBot_QA')
sheet_L1_Cloze = spreadSheet.worksheet("L1_Cloze")
L1_Cloze = sheet_L1_Cloze.get_all_values()
sheet_L2_Cloze = spreadSheet.worksheet("L2_Cloze")
L2_Cloze = sheet_L2_Cloze.get_all_values()
sheet_L3_Cloze = spreadSheet.worksheet("L3_Cloze")
L3_Cloze = sheet_L3_Cloze.get_all_values()

sheet_L1_Reading = spreadSheet.worksheet("L1_Reading")
L1_Reading = sheet_L1_Reading.get_all_values()
sheet_L2_Reading = spreadSheet.worksheet("L2_Reading")
L2_Reading = sheet_L2_Reading.get_all_values()
sheet_L3_Reading = spreadSheet.worksheet("L3_Reading")
L3_Reading = sheet_L3_Reading.get_all_values()
#print(L3_Cloze[0])

def getSheet(Qlevel):   
    if(Qlevel == 3):
        sheet_Reading = L3_Reading
        sheet_Cloze = L3_Cloze 

    elif(Qlevel == 2):
        sheet_Reading = L2_Reading
        sheet_Cloze = L2_Cloze
    else:
        sheet_Reading = L1_Reading
        sheet_Cloze = L1_Cloze
    
    #sheet_Voc = getVoc.getSheet(Qlevel,sh_Q)
    
    return sheet_Reading, sheet_Cloze

def editSheet(data):
    #pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    #pre_sheet = pre_sheet.reset_index(drop=True)
    #print("pre_sheet",pre_sheet)
    #因為reading題型的題庫形式緊接三題連貫題目，就不像之前先打亂隨機取資料
    header = data.columns
    sheet_Q = {}
    for i in range (len(header)):
        sheet_Q[header[i]] = data[header[i]]
    
    return sheet_Q


if __name__ == "__main__":
    level_Q = 1
    data_Reading, data_Cloze = getSheet(level_Q) 
    #sheet_Q = editSheet(data_Cloze)
    print(len(np.transpose([data_Cloze])[0]))
    subindex_Q = random.randrange(1,len(np.transpose([data_Cloze])[0]))
    question = data_Cloze[1][0]
    print("subindex_Q",subindex_Q)
    print(question)
    print("option1 = ",data_Cloze[1][1])
    print("option2 = ",data_Cloze[1][2])
    print("option3 = ",data_Cloze[1][3])

    print("reading",len(np.transpose([data_Reading])[0]))
    subindex_Q = random.randrange(1,len(np.transpose([data_Reading])[0]),3)
    print("subindex_Q",subindex_Q)
    article = data_Reading[subindex_Q][0]
    print("article = ",article)
