# 验证码
import datetime, hashlib, base64, requests, json

class YunTongXin():
    base_url = "https://app.cloopen.com:8883"

    def __init__(self, accountSid, accountToken, appId, templateId):
        self.accountSid = accountSid # 账户id
        self.accountToken = accountToken # 用户令牌
        self.appId = appId # 应用id
        self.templateId = templateId # 模板id

    def get_request_url(self, sig):
        # /2013-12-26/Accounts/{accountSid}/SMS/{funcdes}?sig={SigParameter}

        return self.base_url + f"/2013-12-26/Accounts/{self.accountSid}/SMS/TemplateSMS?sig={sig}"

    def get_timestamp(self):
        # 生成时间戳
        return datetime.datetime.now().strftime(r'%Y%m%d%H%M%S')

    def get_sig(self, timestamp):
        # 生成业务url中的sign
        s = self.accountSid + self.accountToken + timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()
    
    def get_request_header(self, timestamp):
        # 生成请求头
        s = self.accountSid + ":" + timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {
            "Accept": "application/json", 
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": auth
        }
    
    def get_request_body(self, phone, code):
        # 构建请求体
          return {
            "to": phone,
            "appId": self.appId,
            "templateId": self.templateId,
            "datas": [code, "3"]
        } 

    def request_api(self, url, header, body):
        # 发起请求
        res = requests.post(url, headers=header, data=body)
        return res.text
    
    def run(self, phone, code):
        # 获取时间戳
        timestamp = self.get_timestamp()
        # 获取sig
        sig = self.get_sig(timestamp)
        # 获取业务url
        url = self.get_request_url(sig)
        # 获取请求头
        header = self.get_request_header(timestamp)
        # 生成请求体
        body = self.get_request_body(phone, code)
        # 发起请求
        data = self.request_api(url, header, json.dumps(body))
        return data
        

if __name__ == "__main__":
    config = {
        "accountSid": "8a216da87ca23458017cbb94481e0485",
        "accountToken": "07b03bc2e7a34bcc8c7ef9c720e0547d",
        "appId": "8a216da87ca23458017cbb944915048b",
        "templateId": "1"
    }
    a = YunTongXin(**config)
    res = a.run("19825087447", "260801")
    print(res)