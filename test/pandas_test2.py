import numpy as np
import pandas as pd
import pygsheets
import random

GDriveJSON = 'question.json'
GSpreadSheet_Q = 'Chatbot Voc1200'
gc_Q = pygsheets.authorize(service_account_file='question.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1CBYTu0Lnnc0oUSSgTFvM4b6okDCaDrn5lklNxpw2Ms4/edit#gid=1449448532'
sh_P = gc_Q.open_by_url(survey_url_P)
sh_P.worksheet_by_title('L1_Cloze').export(filename='L1_Cloze')
sheet_L1 = pd.read_csv('L1_Cloze.csv') #type: <class 'pandas.core.frame.DataFrame'>

users = np.array(('0',0,0)) #userID,level,point
print("users",users)
userID = '7678329847234fgbfgb'
userID2 = 8979798798
df = pd.read_excel("test.xlsx", header = None)
#df = df.sample(frac =1)
#df = df.reset_index(drop=True)

question = df[0]
optionA = df[1]
optionB = df[2]
optionC = df[3]
optionD = df[4]
feedback = df[5]
answer = df[6]
#np.random.shuffle(df)

print(df)
sheet = {
    "question": question,
    "optionA": optionA,
    "optionB": optionB,
    "optionC": optionC,
    "optionD": optionD,
    "feedback": feedback,
    "answer": answer
}

num = len(sheet["question"])

def setLevel(level):
    users[1] = level

while True:
    if users[0]== '0':
        users[0]=userID
        myResult= ("目前程度切換至Level"+str(int(users[1]))+'\n請任意輸入將開始出題～～')
        #myResult += 
        level = input(myResult)
        setLevel(level)

    else:
        print("users",users)
        for i in range(num):
            subindex_Q = random.randrange(0,len(sheet["question"]),3)
            print(subindex_Q)
            #print(sheet["question"][i])
            print("1:", sheet["optionA"][i], "\n2:", sheet["optionB"][i], "\n3:", sheet["optionC"][i], "\n4:", sheet["optionD"][i], "\n")
            userAns = input("輸入答案:")

            if(userAns != str(sheet["answer"][i])):
                print(type(userAns),type(sheet["answer"][i]),userAns,sheet["answer"][i])
                print(sheet["feedback"][i])

