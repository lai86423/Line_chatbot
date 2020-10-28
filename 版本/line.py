import gspread
from oauth2client.service_account import ServiceAccountCredentials

auth_json_path = 'JSON.json'
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_json_path,scopes)
client = gspread.authorize(credentials)
spreadsheet_key = '194F1eOLPBick8Veoti9XtXEnypQgcIK6_dc9LcFUJDc' 
# sheet = client.open_by_key(spreadsheet_key).worksheet('L1_voc')
sheet = client.open('cilab_ChatBot_QA').sheet1

print('For all files in this account:')
for s in client.openall():
    print('\t'+s.title)

print(sheet.row_values(2)) 
print(sheet.row_values(3)) 
print(sheet.row_values(4)[1])