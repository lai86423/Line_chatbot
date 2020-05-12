var linebot = require('linebot');
var express = require('express');
var translate = require('google-translate-api');

var bot = linebot({
  channelId: '請輸入LineBot的channelId',
  channelSecret: '請輸入LineBot的channelSecret',
  channelAccessToken: '請輸入LineBot的channelAccessToken'
});

var users=[];
//預設翻譯語言是英文
var defaultLangNum=2;

//以下各國語言陣列，可自行加減，語言代碼參照，請參考以下連結
//https://cloud.google.com/translate/docs/languages
var languages=[
    {language: '繁體中文', code: 'zh-tw'},
    {language: '簡體中文', code: 'zh-cn'},
    {language: '英文', code: 'en'},
    {language: '日文', code: 'ja'},
    {language: '韓文', code: 'ko'},
    {language: '泰文', code: 'th'},
    {language: '越南文', code: 'vi'},
    {language: '印尼文', code: 'id'},
    {language: '德文', code: 'de'},
    {language: '法文', code: 'fr'},
    {language: '俄文', code: 'ru'}
];

//取得第一次交談時的歡迎詞
var welcomeStr=getWelcomeStr();

bot.on('message', function(event) {
   var myReply='';
   var myId=event.source.userId;
   if (event.message.type === 'text') {
      if (users[myId]===undefined){
         users[myId]=[];
         users[myId].userId=myId;
         users[myId].defaultLangNum=defaultLangNum;
         myReply=welcomeStr+'目前的設定的翻譯語言為：'+languages[users[myId].defaultLangNum].language;
      }else if(event.message.text==='?'){
         myReply=welcomeStr+'目前的設定的翻譯語言為：'+languages[users[myId].defaultLangNum].language;
      }else if(!isNaN(event.message.text)){
         if (Number(event.message.text)<languages.length)
            setLanguage(myId,Number(event.message.text));
      }else{
         translate(event.message.text, {to: languages[users[myId].defaultLangNum].code}).then(res => {
         bot.push(myId,res.text);
         }).catch(err => {
            console.error(err);
         });
      }
      event.reply(myReply).then(function(data) {
         // success 
         console.log(myReply);
      }).catch(function(error){   
         // error 
         console.log('error');
      });
   }
});


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

//此為設定翻譯語言之函式
function setLanguage(userId,myLangNum){
   users[userId].defaultLangNum=myLangNum;
   bot.push(userId,'翻譯的語言已設定為：'+languages[myLangNum].language);
}

//此為處理語言設定字串之函式
function getWelcomeStr(){
   var myResult='您好，歡迎來到吉哥的即時翻譯LineBot，讓您用Line就可以翻譯各國語言。您可以輸入各國語言，轉換成您想要翻譯的語言，所以，請先設定您想要轉換成的語言，輸入數字即可設定完成：\n';
   for(var i=0;i<languages.length;i++){
      myResult+=(i+'：'+languages[i].language+'\n');
   }
   myResult+='?：列出語言設定指令\n';
   return myResult;
}

const app = express();
const linebotParser = bot.parser();
app.post('/', linebotParser);

//因為 express 預設走 port 3000，而 heroku 上預設卻不是，要透過下列程式轉換
var server = app.listen(process.env.PORT || 8080, function() {
  var port = server.address().port;
  console.log("App now running on port", port);
});