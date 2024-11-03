import subprocess
import os
class CmdExec():
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        self.is_root = (os.getuid() == 0)
    def run(self, command:str,use_sudo:bool=False):
        if use_sudo:
            if self.is_root:
                return self._run(command)
            else:
                return self._run_with_sudo(command)
        else:
            if self.is_root:
                return self._run_with_sudo_as_user(command)
            return self._run(command)
    def _run(self, command:str):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode,result.stdout.strip()
    def _run_with_sudo(self, command:str):
        command = f'echo {self.password} | sudo -S {command}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode,result.stdout.strip()
    def _run_with_sudo_as_user(self, command:str):
        command = f'echo {self.password} | sudo -S -u {self.username} {command}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode,result.stdout.strip()
    
# 示例用法
if __name__ == "__main__":
    from auth import Auth
    auth = Auth("hao","123")
    ret,id,session_id  = auth.verify_token()
    if ret:
        cmd_exec = CmdExec(auth.get_username(),auth.get_password())
        print(cmd_exec.run("whoami"))
    else:
        print("Auth failed")