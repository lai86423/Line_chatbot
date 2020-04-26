//以下的四列require裡的內容，請確認是否已經用npm裝進node.js
var linebot = require('linebot');
var express = require('express');
var google = require('googleapis');
var googleAuth = require('google-auth-library');

//以下的引號內請輸入申請LineBot取得的各項資料，逗號及引號都不能刪掉
var bot = linebot({
  channelId: '請輸入LineBot的channelId',
  channelSecret: '請輸入LineBot的channelSecret',
  channelAccessToken: '請輸入LineBot的channelAccessToken'
});

//底下輸入client_secret.json檔案的內容
var myClientSecret=請將client_secret.json檔案的內容放在這裡，前後不能加引號

var auth = new googleAuth();
var oauth2Client = new auth.OAuth2(myClientSecret.installed.client_id,myClientSecret.installed.client_secret, myClientSecret.installed.redirect_uris[0]);

//底下輸入sheetsapi.json檔案的內容
oauth2Client.credentials =請將sheetsapi.json檔案的內容放在這裡，前後不能加引號

//試算表的ID，引號不能刪掉
var mySheetId='請輸入試算表的ID編號';

var title='';
var users=[];

var totalSteps=0;
var myQuestions=[];



//程式啟動後會去讀取試算表的歡迎詞工作表的內容
getTitle();
//程式啟動後會去讀取試算表的問題的工作表的內容
getQuestions();


//取得歡迎詞內容的函式
function getTitle() {
   var sheets = google.sheets('v4');
   sheets.spreadsheets.values.get({
      auth: oauth2Client,
      spreadsheetId: mySheetId,
      range:encodeURI('歡迎詞'),
   }, function(err, response) {
      if (err) {
         console.log('讀取問題檔的API產生問題：' + err);
         return;
      }
      title= response.values[0][0];
      console.log('title已下載完畢！');
   });
} 

//取得線上測驗問題的函式
function getQuestions() {
   var sheets = google.sheets('v4');
   sheets.spreadsheets.values.get({
      auth: oauth2Client,
      spreadsheetId: mySheetId,
      range:encodeURI('問題'),
   }, function(err, response) {
      if (err) {
         console.log('讀取問題檔的API產生問題：' + err);
         return;
      }
      var rows = response.values;
      if (rows.length == 0) {
         console.log('No data found.');
      } else {
         myQuestions=rows;
         totalSteps=myQuestions.length;
         console.log('要問的問題已下載完畢！');
      }
   });
}


//LineBot收到user的文字訊息時的處理函式
bot.on('message', function(event) {
   if (event.message.type === 'text') {
      var myId=event.source.userId;
      if (users[myId]==undefined){
         users[myId]=[];
         users[myId].userId=event.source.userId;
         users[myId].step=-1;
         users[myId].rightAns=0;
         users[myId].replies=[];
         users[myId].replies[0]='';
         users[myId].replies[1]=new Date();
         getDisplayName(event);
         sendMessage(event,title+'本次測驗共有'+totalSteps+'題：');
         setTimeout(function() {
            pushStepQuestion(users[myId].userId);
         }, 2000);
      }
      else{
         if(!isNaN(event.message.text)){
            checkAnswer(users[myId].userId,event.message.text);
         }else{
            sendMessage(event,'請用阿拉伯數字選擇答案！');
         }
      }
   }
});


//取得user的使用者名稱
function getDisplayName(eve){
   bot.getUserProfile(eve.source.userId);
   eve.source.profile().then(function (profile) {
      users[eve.source.userId].replies[0]=profile.displayName;
   }).catch(function (error) {
       // error 
   });
}


//這是將測驗結果儲存進試算表的函式
function appendMyRow(userId) {
   var request = {
      auth: oauth2Client,
      spreadsheetId: mySheetId,
      range:encodeURI('測驗結果'),
      insertDataOption: 'INSERT_ROWS',
      valueInputOption: 'RAW',
      resource: {
        "values": [
          users[userId].replies
        ]
      }
   };
   var sheets = google.sheets('v4');
   sheets.spreadsheets.values.append(request, function(err, response) {
      if (err) {
         console.log('The API returned an error: ' + err);
         return;
      }
   });
}


//檢查答案是否正確的函式
function checkAnswer(whoId,myAns){
   var myStep=users[whoId].step;
   if (myStep<totalSteps){
      users[whoId].answers=[];
      users[whoId].answers[myStep]=myAns;
      users[whoId].replies[myStep*2+2]=Number(myAns);
      if (myAns===myQuestions[myStep][6]){
         users[whoId].replies[myStep*2+3]=1;
         //以下一行為傳送貼圖程式，第一個參數是要傳送的對象，第二個為貼圖的package ID，第三個參數為貼圖ID
         sendSticker(whoId,1,13);
         users[whoId].rightAns++;
      }else{
         users[whoId].replies[myStep*2+3]=0;
         //以下一行為傳送貼圖程式，第一個參數是要傳送的對象，第二個為貼圖的package ID，第三個參數為貼圖ID
         sendSticker(whoId,1,3);
         bot.push(whoId,myQuestions[myStep][5]);
      }
      myStep++;
      if (myStep>=totalSteps){
         users[whoId].replies[myStep*2+2]=users[whoId].rightAns;
    appendMyRow(whoId);
         setTimeout(function() {
            bot.push(whoId,'測驗完畢！'+totalSteps+'題共答對'+users[whoId].rightAns+'題！');
            delete users[whoId];
         },700); 
      }else{
         setTimeout(function() {
            pushStepQuestion(whoId);
         }, 1000);
      }
   }
}

//送出貼圖的函式
function sendSticker(to,pkg_id,stk_id){
   var messageData = {
      type: 'sticker',
      packageId: pkg_id,
      stickerId: stk_id
   };
   bot.push(to,messageData);
}

//發問問題的函式
function pushStepQuestion(to){
   users[to].step++;
   var myStep=users[to].step;
   var myMsg='第'+(myStep+1)+'題：\n';
   myMsg+=(myQuestions[myStep][0]+'\n');
   for (var i=1;i<5;i++){ 
      myMsg+=('('+i+')'+myQuestions[myStep][i]+' ');
   }
   bot.push(to,myMsg);
}

//傳送訊息的函式
function sendMessage(eve,msg){
   eve.reply(msg).then(function(data) {
      // success 
      return true;
   }).catch(function(error) {
      // error 
      return false;
   });
}


const app = express();
const linebotParser = bot.parser();
app.post('/', linebotParser);

//因為 express 預設走 port 3000，而 heroku 上預設卻不是，要透過下列程式轉換
var server = app.listen(process.env.PORT || 8080, function() {
  var port = server.address().port;
  console.log("App now running on port", port);
});