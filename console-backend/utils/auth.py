import subprocess

class Auth():
    def __init__(self):
        self._token = {"username": "", "password": ""}
        self._is_login = False
    def verify_token(self,username,password):
        try:
            if not username or not password:
                raise ValueError("Username and password cannot be empty")
            # 使用命令行检查密码
            command = f'echo {password} | sudo -S -u {username} true'
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if(result.returncode == 0):
                print("Password is correct")
                self._token['username'] = username
                self._token['password'] = password
                self._is_login = True
                command = f'echo {password}|sudo -S -u {username} -k' # 清除sudo缓存 
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error: {e}")
            return False
    def isLogin(self):
        return self._is_login
    