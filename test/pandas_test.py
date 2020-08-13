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
#print(type(sheet["chinese"]))
q_num = len(sheet["chinese"])
q_index = [random.randint(1, q_num) for _ in range(3)]
#print(q_index)
for i in range (3):
    q_chinese = sheet["chinese"][q_index[i]]
    q_english = sheet["english"][q_index[i]]
    
    q_prefix = sheet["prefix"][q_index[i]]
    q_part = sheet["part"][q_index[i]]
    q_part2 = sheet["part2"][q_index[i]]
    print(q_chinese,q_english,q_prefix,q_part,q_part2)

    #get same title voc index 
    same_prefix_index = sheet["prefix"].index[sheet["prefix"] == q_prefix]
    #print(same_prefix_index)

    #get same part of speech voc index 
    same_part_index = sheet["part"].index[sheet["part"] == q_part]
    same_part_index2 = sheet["part2"].index[sheet["part2"] == q_part]

    #get same title and part of speech voc index
    same_index = set(same_prefix_index) & set(same_part_index)
    #print("same_index",same_index)

    if str(q_part2)!='nan':
        print("Not nan but same part--",q_part2)
        same_part2_index = sheet["part"].index[sheet["part"] == q_part2]
        same_part2_index2 = sheet["part2"].index[sheet["part2"] == q_part2]
        print("same_part2_index",same_part2_index)
        print("same_part2_index2",same_part2_index2)
        same_index2 = set(same_prefix_index) & set(same_part2_index)
        same_index3 = set(same_prefix_index) & set(same_part2_index2)
        print("same_index2",same_index2)
        print("same_index3",same_index3)

    #print(same_part_index)
    #for i in range (len(same_part_index2)):   
        #print("same_part_index",sheet["english"][same_part_index[i]])
        #print("same_part_index2",sheet["english"][same_part_index2[i]])

    

    #get two voc from same_index
    solu_index = random.sample(same_index, 2) 
    solu_prefix = sheet["english"][solu_index[0]]
    solu_prefix2 = sheet["english"][solu_index[1]]
    #print(solu_prefix,solu_prefix2) 




    # same_prefix = list(sheet["prefix"]).index(prefix)
    # same_prefix = [i for i,x in enumerate(list(sheet["prefix"])) if sheet["prefix"]==prefix]
    # print("prefix same = ",same_prefix)

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

