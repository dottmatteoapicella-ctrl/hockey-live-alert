import json
import urllib.request
import urllib.error

class Telegram:
    def __init__(self,token,chat):
        self.token=token
        self.chat=chat
    def call(self,method,fields):
        data=json.dumps({"chat_id":self.chat,**fields}).encode()
        req=urllib.request.Request("https://api.telegram.org/bot"+self.token+"/"+method,data=data,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=20) as res:
                result=json.load(res)
        except (OSError,ValueError):
            return None
        return result.get("result") if isinstance(result,dict) and result.get("ok") is True else None
    def send(self,text):
        result=self.call("sendMessage",{"text":text})
        mid = result.get("message_id") if isinstance(result,dict) else None
        return mid if type(mid) is int and mid > 0 else None
    def edit(self,message_id,text):
        return self.call("editMessageText",{"message_id":message_id,"text":text}) is not None

