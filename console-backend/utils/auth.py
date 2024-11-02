import subprocess
import uuid
import time
from utils.cmd_exec import CmdExec
import os
import pam
class Auth():
    def __init__(self,username:str,password:str):
        self._token = {"username": "", "password": "", "device_id": ""}
        self._token['username'] = username
        self._token['password'] = password
        self._token['device_id'] =  str(uuid.uuid4())
        self._is_login = False
        self._auth_timestamp = time.time()
        self._cmd_exec = CmdExec(self._token['username'],self._token['password'])
    def verify_token(self):
        try:
            if not self._token['username'] or not self._token['password']:
                raise ValueError("Username and password cannot be empty")
            p = pam.pam()
            if(p.authenticate(self._token['username'], self._token['password'])):
                self._is_login = True
                return True,self._token['device_id']
            return False,""
        except Exception as e:
            print(f"Error: {e}")
            return False,""
    def isLogin(self):
        return self._is_login
    def get_device_id(self):
        return self._token['device_id']
    def get_username(self):
        return self._token['username']
    def is_timeout(self):
        return time.time() - self._auth_timestamp > 3600*24
    def get_password(self):
        return self._token['password']

if __name__ == "__main__":
    auth = Auth("hao","123")
    ret,id = auth.verify_token()
    print(ret,id)
    auth = Auth("hao","23")
    ret,id = auth.verify_token() 
    print(ret,id)  