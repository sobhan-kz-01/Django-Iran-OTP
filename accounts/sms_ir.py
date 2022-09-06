import json
import requests
from typing import List,Dict
from django.conf import settings


class SMSApi:
    def __init__(self) -> None:
        """
         SMS.IR API

             token = (API Instance).get_token()
             (API Instance).send_ultra_fast_send(to:str,text:str,token:str,template_id:str) -> response
        """
        __auth = getattr(settings,'AUTH_SERVICE')
        self.user_key = __auth['SMS.IR']['user_api_key']
        self.secret_key = __auth['SMS.IR']['secret_key']
        self.template_id = __auth['SMS.IR']['otp_template_id']
        self.token_url = 'http://RestfulSms.com/api/Token'
        self.credit_url = 'http://RestfulSms.com/api/credit'
        self.ultra_fast_send_url = 'http://RestfulSms.com/api/UltraFastSend'
        self.verify_url = 'http://RestfulSms.com/api/VerificationCode'
    def ultra_fast_send(self,parameter_array:List[Dict],mobile:str,template_id:str,token:str):
        headers = {
        "Content-Type": "application/json",
        'x-sms-ir-secure-token': token
    }
        body = {
            "ParameterArray": parameter_array,
            "Mobile": mobile,
            "TemplateId": template_id
        }
        response = requests.post(self.ultra_fast_send_url, data=json.dumps(body),
                                headers=headers)

        return response
    def get_token(self) :
        headers = {
        "Content-Type": "application/json",
        }
        body = {
            "UserApiKey": self.user_key,
            "SecretKey": self.secret_key
        }
        response = requests.post(self.token_url, data=json.dumps(body), headers=headers)
        if response.status_code is 201:
            if response.json()['IsSuccessful'] is True:
                secure_token = response.json()['TokenKey']
                return secure_token
        return None
    def get_credit(self,token:str=''):
       
        headers = {
            "Content-Type": "application/json",
            'x-sms-ir-secure-token': token
        }
        response = requests.get(self.credit_url, headers=headers)
        return response


    def verify_code(self,code:str='', mobile_number:str='', token:str=''):
        headers = {
            "Content-Type": "application/json",
            'x-sms-ir-secure-token': token
        }
        body = {
            "Code": code,
            "MobileNumber": mobile_number
        }
        response = requests.post(self.token_url, data=json.dumps(body),
                                headers=headers)

        return response


    def send_verify(self,to:str,text:str,token:str):
        return self.verify_code(code=text,mobile_number=to,token=token)    

    def send_ultra_fast_send(self,to:str,text:str,token:str):
        return self.ultra_fast_send(parameter_array=[{"Parameter": "VerificationCode","ParameterValue": text}],mobile=to,template_id=self.template_id,token=token)