import numpy as np
import pandas as pd
import gspread
#import pygsheets
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("question.json", scope)
client = gspread.authorize(creds)
spreadSheet = client.open("Chatbot Voc1200")
user_sheet = spreadSheet.worksheet("Chatbot Voc1200")
user_data = user_sheet.get_all_values()
#print("id\n",user_sheet)
user_data = user_sheet.get_all_values()
print("user_data",user_data)



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

