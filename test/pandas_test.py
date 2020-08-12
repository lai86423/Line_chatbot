import numpy as np
import pandas as pd
import pygsheets
import random

GDriveJSON = 'question.json'
GSpreadSheet_Q = 'Chatbot Voc1200'
gc_Q = pygsheets.authorize(service_account_file='question.json')
survey_url_P = 'https://docs.google.com/spreadsheets/d/1G5gy7173hk3kcp8AFGM8EOUvb7Wa-KmU4V0dHJQQYEk/edit#gid=831684372'
sh_P = gc_Q.open_by_url(survey_url_P)
sh_P.worksheet_by_title('L1(628)').export(filename='L1')
sheet_L1 = pd.read_csv('L1.csv') #type: <class 'pandas.core.frame.DataFrame'>

chinese = sheet_L1.iloc[:,0]
english = sheet_L1.iloc[:,1]
part = sheet_L1.iloc[:,2]
part2 = sheet_L1.iloc[:,3]
prefix = sheet_L1.iloc[:,4]

sheet = {
        "chinese": chinese,
        "english": english,
        "part": part,
        "part2": part2,
        "prefix": prefix
    }
print(type(sheet["chinese"]))
qNum_L = len(sheet["chinese"])
print(qNum_L)
rnds = [random.randint(1, qNum_L) for _ in range(3)]
print(rnds)
for i in range (3):
    print(sheet["chinese"][rnds[i]])
    print(sheet["english"][rnds[i]])
    prefix = sheet["prefix"][rnds[i]]
    print(prefix)
    print(sheet["prefix"].index[sheet["prefix"]==prefix])
    same_prefix = list(sheet["prefix"]).index(prefix)

    print("prefix same = ",same_prefix)

# while True:
     

# users = np.array(('0',0,0)) #userID,level,point
# print("users",users)
# userID = '7678329847234fgbfgb'
# userID2 = 8979798798
# df = pd.read_excel("test.xlsx", header = None)
# question = df[0]
# optionA = df[1]
# optionB = df[2]
# optionC = df[3]
# optionD = df[4]
# feedback = df[5]
# answer = df[6]
# #np.random.shuffle(df)
# df = df.sample(frac =1)
# print(df)
# sheet = {
#     "question": question,
#     "optionA": optionA,
#     "optionB": optionB,
#     "optionC": optionC,
#     "optionD": optionD,
#     "feedback": feedback,
#     "answer": answer
# }
# num = len(sheet["question"])

# def setLevel(level):
#     users[1] = level

# while True:
#     if users[0]== '0':
#         users[0]=userID
#         myResult= ("目前程度切換至Level"+str(int(users[1]))+'\n請任意輸入將開始出題～～')
#         #myResult += 
#         level = input(myResult)
#         setLevel(level)

#     else:
#         print("users",users)
#         for i in range(num):
#             print(sheet["question"][i])
#             print("1:", sheet["optionA"][i], "\n2:", sheet["optionB"][i], "\n3:", sheet["optionC"][i], "\n4:", sheet["optionD"][i], "\n")
#             userAns = input("輸入答案:")

#             if(userAns != str(sheet["answer"][i])):
#                 print(type(userAns),type(sheet["answer"][i]),userAns,sheet["answer"][i])
#                 print(sheet["feedback"][i])

