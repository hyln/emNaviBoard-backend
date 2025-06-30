import subprocess
import os
import re
from emNaviBase.utils.cmd_exec import CmdExec
# from cmd_exec import CmdExec

class EnvVariableManager:
    def __init__(self, cmd_exec:CmdExec,file_path='/etc/bash.bashrc'):
        self.file_path = file_path
        self.cmd_exec = cmd_exec
        self.ensure_env_block()
    
    def ensure_env_block(self):
        start_marker = "# emnavibase-start"
        end_marker = "# emnavibase-end"

        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        start_exists = any(start_marker in line for line in lines)
        end_exists = any(end_marker in line for line in lines)

        if not start_exists or not end_exists:
            with open(self.file_path, 'a') as f:
                if not start_exists:
                    f.write(f"\n{start_marker}\n")
                if not end_exists:
                    f.write(f"{end_marker}\n")

    def add_env_variable(self, key, value):
        if not self.variable_exists(key):
            command = f'tee -a {self.file_path} | sed -i "/# emnavibase-end/i export {key}=\\"{value}\\"" {self.file_path}'
            print(command)
            try:
                self.cmd_exec.run(command,use_sudo=True)
                print(f"Variable '{key}' added successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error adding variable: {e}")
            self.sync_changes()
        else:
            print(f"Variable '{key}' already exists.")

    def modify_env_variable(self, key, new_value):
        start_tag = '# emnavibase-start'
        end_tag = '# emnavibase-end'
        temp_file_path = '/tmp/temp_env_file'

        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        in_block = False
        modified = False

        with open(temp_file_path, 'w') as f:
            for line in lines:
                stripped = line.strip()

                if stripped == start_tag:
                    in_block = True
                    f.write(line)
                    continue
                elif stripped == end_tag:
                    in_block = False
                    f.write(line)
                    continue

                if in_block and re.match(rf'export {key}=', stripped):
                    f.write(f'export {key}="{new_value}"\n')
                    modified = True
                else:
                    f.write(line)

        if not modified:
            print(f"Variable '{key}' not found in the block.")
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

        start_marker = "# emnavibase-start"
        end_marker = "# emnavibase-end"

        start_index = None
        end_index = None

        for i, line in enumerate(lines):
            if start_marker in line:
                start_index = i
            if end_marker in line:
                end_index = i

        del_line_index = 0
        if start_index is not None and end_index is not None and start_index < end_index:
            lines = lines[:start_index + 1] + lines[end_index:]
        for i, line in enumerate(lines):
            if line.lstrip().startswith(f'export {key}='):
                    lines.pop(i)
                    break
        start_marker = "# emnavibase-start"
        end_marker = "# emnavibase-end"
        
        with open(temp_file_path, 'w') as f:
            for line in lines:
                if not line.lstrip().startswith(f'export {key}='):
                    f.write(line)
        self._replace_env_file(temp_file_path)
 
    def find_env_variable(self, key):
        with open(self.file_path, 'r') as f:
            in_block = False
            for line in f:
                stripped = line.strip()
                if stripped == '# emnavibase-start':
                    in_block = True
                elif stripped == '# emnavibase-end':
                    in_block = False
                elif in_block and stripped.startswith(f'export {key}='):
                    _, value = stripped.split('=', 1)
                    value = value.strip().strip('"')
                    return True, value
        return False, ""
    def variable_exists(self, key):
        ret,value = self.find_env_variable(key)
        return ret

    def sync_changes(self):
        subprocess.run(['sync'])

# 示例用法
if __name__ == "__main__":
    manager = EnvVariableManager(CmdExec("hao","123"),"/media/hao/WorkSpace1/emnaviBoard/emNaviBoard-backend/emNaviBase/utils/test_env.txt")
    manager.add_env_variable('NEW_VAR1', 'some_value')
    manager.add_env_variable('NEW_VAR2', 'some_value')
    manager.add_env_variable('NEW_VAR3', 'some_value')

    manager.modify_env_variable('NEW_VAR1', 'new_value')
    manager.delete_env_variable('NEW_VAR')
