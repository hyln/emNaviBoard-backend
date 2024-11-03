import subprocess
import os
from emNaviBase.utils.cmd_exec import CmdExec
class EnvVariableManager:
    def __init__(self, cmd_exec:CmdExec,file_path='/etc/environment'):
        self.file_path = file_path
        self.cmd_exec = cmd_exec

    def add_env_variable(self, key, value):
        if not self.variable_exists(key):
            command = f'echo \'{key}="{value}"\' | sudo tee -a {self.file_path}'
            try:
                self.cmd_exec.run(command,use_sudo=True)
                print(f"Variable '{key}' added successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error adding variable: {e}")
            self.sync_changes()
        else:
            print(f"Variable '{key}' already exists.")

    def modify_env_variable(self, key, new_value):
        if not self.variable_exists(key):
            print(f"Variable '{key}' does not exist.")
            return
        temp_file_path = '/tmp/temp_env_file'
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        with open(temp_file_path, 'w') as f:
            for line in lines:
                if line.startswith(key):
                    f.write(f'{key}="{new_value}"\n')
                else:
                    f.write(line)
        self._replace_env_file(temp_file_path)

    def _replace_env_file(self, temp_file_path):
        # 使用 sudo 替换原文件
        command = f'mv {temp_file_path} {self.file_path}'
        try:
            ret,status = self.cmd_exec.run(command,use_sudo=True)
            self.sync_changes()
        except subprocess.CalledProcessError as e:
            print(f"Error modifying variable: {e}")
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    def delete_env_variable(self, key):
        if not self.variable_exists(key):
            print(f"Variable '{key}' does not exist.")
            return
        temp_file_path = '/tmp/temp_env_file'
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
        with open(temp_file_path, 'w') as f:
            for line in lines:
                if not line.startswith(key):
                    f.write(line)
        self._replace_env_file(temp_file_path)
 
    def find_env_variable(self, key):
        # 不需要sudo权限
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.startswith(key):
                _, value = line.split('=', 1)  # 从 = 处分割，取后半部分
                value = value.strip().strip('"')  # 去除两边的空白和引号
                return True,value
        return False,""
    def variable_exists(self, key):
        ret,value = self.find_env_variable(key)
        return ret

    def sync_changes(self):
        subprocess.run(['sync'])

# 示例用法
if __name__ == "__main__":
    manager = EnvVariableManager(CmdExec("hao","123"))
    manager.add_env_variable('NEW_VAR', 'some_value')
    manager.modify_env_variable('NEW_VAR', 'new_value')
    manager.delete_env_variable('NEW_VAR')
