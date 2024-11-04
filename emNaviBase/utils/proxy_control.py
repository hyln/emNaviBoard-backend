import subprocess
from emNaviBase.utils.env_control import EnvVariableManager
from emNaviBase.utils.cmd_exec import CmdExec
class ProxyControl:
    def __init__(self, username:str, password:str):
        self.cmd_exec = CmdExec(username,password)
        self.env_var_manager =EnvVariableManager(self.cmd_exec)
    def get_proxy_status(self):
        status_count = 0
        addr = ""
        if(self.env_var_manager.variable_exists("http_proxy")):
            status_count += 1
            _,addr = self.env_var_manager.find_env_variable("http_proxy")
            
        if(self.env_var_manager.variable_exists("https_proxy")):
            status_count += 1
        if(self._get_gnome_proxy_status() == "manual"):
            status_count += 1  
        if(status_count == 0):
            return "off",""
        elif(status_count == 3):
            return "on",addr
        else:
            return "partial_on",addr
    def set_proxy(self, enable=False,host="127.0.0.1", port=7890):
        self._set_shell_proxy(enable,host,port)
        self._set_gnome_proxy(enable,host,port)
    def _set_shell_proxy(self, enable, host="127.0.0.1", port=7890):
        if enable:
            self.env_var_manager.add_env_variable("http_proxy", f"http://{host}:{port}")
            self.env_var_manager.add_env_variable("https_proxy", f"http://{host}:{port}")
        else:
            self.env_var_manager.delete_env_variable("http_proxy")
            self.env_var_manager.delete_env_variable("https_proxy")            
    def _set_gnome_proxy(self, enable, host="127.0.0.1", port=7890):
        if enable: # 启动代理 
            commands = [
                f"dbus-launch /usr/bin/gsettings set org.gnome.system.proxy.http host {host}",
                f"dbus-launch /usr/bin/gsettings set org.gnome.system.proxy.http port {port}",
                f"dbus-launch /usr/bin/gsettings set org.gnome.system.proxy.https host {host}",
                f"dbus-launch /usr/bin/gsettings set org.gnome.system.proxy.https port {port}",
                "dbus-launch /usr/bin/gsettings set org.gnome.system.proxy mode manual",
            ]
            for command in commands:
                self.cmd_exec.run(command,use_sudo=False)   
        else: # 关闭代理
            command = "dbus-launch /usr/bin/gsettings set org.gnome.system.proxy mode none"
            self.cmd_exec.run(command,use_sudo=False)
    def _get_gnome_proxy_status(self):
        command = "/usr/bin/gsettings get org.gnome.system.proxy mode"
        ret, status = self.cmd_exec.run(command,use_sudo=False)
        return status.replace("'","")

if __name__ == "__main__":
    proxy_control = ProxyControl()
    proxy_control._set_shell_proxy(False)
    print(proxy_control.get_proxy_status())

    # proxy_control.set_proxy("http://
