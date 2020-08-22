import numpy as np
import pandas as pd
import pygsheets
import random

GDriveJSON = 'question.json'
GSpreadSheet_P = 'cilab_ChatBot_puzzle'
gc_Q= pygsheets.authorize(service_account_file='question.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1nVIgWGQJRIQtMtZSv1HxyDb5FvthBNc0duN4Rlra8to/edit#gid=1732714016'
sh_P = gc_Q.open_by_url(survey_url_P)
sh_P.worksheet_by_title('d0').export(filename='d0')
sh_P.worksheet_by_title('r0').export(filename='r0')
sheet_d0 = pd.read_csv('d0.csv') #type: <class 'pandas.core.frame.DataFrame'>
sheet_r0 = pd.read_csv('r0.csv') 
#print(sheet_d0,sheet_r0)
##----------------------------------------------------------------------------------
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

def editSheet(data):
    #pre_sheet = data.sample(frac =1,random_state=1) #Random打亂資料再取n筆題 
    print("header",data.columns)
    header = data.columns
    sheet_P = {}
    for i in range (len(header)):
        sheet_P[header[i]] = data[header[i]]
    return sheet_P

def smallpuzzle(id, sheet):
    id_four = id[0:3]
    #print(sheet["a-descriptionID"][sheet["a-descriptionID"] == id])
    same_id_index = sheet["a-descriptionID"].index[sheet["a-descriptionID"] == id]
    print(same_id_index)

if __name__ == "__main__":
    #sheet_d, sheet_r = getSheet_P(1)
    smallpuzzle('d00000',sheet_d0)

    #sheet_P = editSheet(sheet_d)

