
import subprocess
import re
from .auth import Auth
from .cmd_exec import CmdExec
class NetworkControl():
    def __init__(self,username:str, password:str) -> None:
        self.cmd_exec = CmdExec(username,password)
        ret,host_name = self.cmd_exec.run("hostname")
        self._ap_wifi_name = host_name
        self._wifi_device = "wlan0"
        self._ap_name = "wifi_ap_emnavi" 

    def set_auth(self,auth:Auth):
        pass

    def parse_wifi_output(self, output):
        wifi_info = []

        # 拆分 Cell 块
        cells = re.split(r'\bCell \d+ - ', output)
        for cell in cells[1:]:  # 跳过第一个空块

            ssid_match = re.search(r'ESSID:"(.*?)"', cell)
            signal_match = re.search(r'Signal level[:=]-?\d+\.?\d*\s*dBm', cell)
            signal_value = re.search(r'Signal level[:=](-?\d+\.?\d*)\s*dBm', cell)
            freq_match = re.search(r'Frequency[=: ]([\d.]+)\s*GHz\s*\(Channel\s*(\d+)\)', cell)
            key_match = re.search(r'Encryption key:(on|off)', cell, re.IGNORECASE)

            # 默认值
            ssid = ssid_match.group(1) if ssid_match else "<hidden>"
            signal = signal_value.group(1) + " dBm" if signal_value else "N/A"
            channel = freq_match.group(2) if freq_match else "N/A"
            active = 'yes' if key_match and key_match.group(1).lower() == 'on' else 'no'

            # 判断加密方式（尽量获取 WPA/WPA2/WPA3）
            if 'WPA3' in cell:
                security = 'WPA3'
            elif 'WPA2' in cell:
                security = 'WPA2'
            elif 'WPA Version 1' in cell or 'WPA ' in cell:
                security = 'WPA'
            elif 'Encryption key:off' in cell:
                security = 'Open'
            else:
                security = 'Unknown'
            active = 'no'
            wifi_info.append({
                'ssid': ssid,
                'signal': int(signal.split(" ")[0]),
                'channel': channel,
                'active': active,
                'security': security
            })
            # Sort Wi-Fi information by signal strength in descending order
            wifi_info.sort(key=lambda x: x['signal'], reverse=True)

        return wifi_info
    def get_ap_wifi_name(self):
        return self._ap_wifi_name
    def get_current_mode(self):
        try:
            ret,result = self.cmd_exec.run("nmcli -t -f NAME,TYPE connection show",use_sudo=True)
            if(self._ap_name in result):
                return "ap"
            else:
                return "sta"
        except Exception as e:
            print(f"An error occurred: {e}")
            return "unknown"

    def wifi_rescan(self):
        # 大概每10秒可刷新一次
        mode = self.get_current_mode()
        if(mode == "ap"):
            print("In AP mode, can't rescan wifi")
            return False
        elif(mode == "sta"):
            ret,_ = self.cmd_exec.run("nmcli device wifi rescan",use_sudo=True)
            print("Rescanning Wi-Fi")
            return True
    
    def clear_all_wifi_connect(self):
        try:
            ret,result = self.cmd_exec.run("nmcli -t -f NAME,TYPE connection show",use_sudo=True)
            connections = result.split('\n')

            # Delete each Wi-Fi connection
            for connection in connections:
                name, conn_type = connection.split(':')
                if conn_type == '802-11-wireless':  # Ensure the connection type is Wi-Fi
                    command = f"nmcli connection delete {name}"
                    ret,result = self.cmd_exec.run(command,use_sudo=True)
                    print(f"Deleted Wi-Fi connection: {name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def start_ap_mode(self):
        ap_device_name= self._ap_name
        # 检测是否已经存在该连接

        cmd_check_connection = f"nmcli connection show | grep {ap_device_name}"
        ret,result = self.cmd_exec.run(cmd_check_connection,use_sudo=True)
        if ret == 0:
            print(f"connection {ap_device_name}  already exists")  
            cmd_delete_connection = f"nmcli connection delete {ap_device_name}" 
            ret,result = self.cmd_exec.run(cmd_delete_connection,use_sudo=True)   
            if ret != 0:
                print("connection delete failed")
                return False
        command_5_list = [
            f"nmcli con add type wifi ifname wlan0 mode ap con-name {ap_device_name} ssid {self._ap_wifi_name }",
            f"nmcli con modify {ap_device_name} 802-11-wireless.band a",
            f"nmcli con modify {ap_device_name} 802-11-wireless.channel 149",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.key-mgmt wpa-psk",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.proto rsn",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.group ccmp",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.pairwise ccmp",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.psk 12341234",
            f"nmcli con modify {ap_device_name} ipv4.addresses 192.168.109.1/24",
            f"nmcli con modify {ap_device_name} ipv4.gateway 192.168.109.1",
            f"nmcli con modify {ap_device_name} ipv4.method shared",
            f"nmcli con up {ap_device_name}"
        ]

        command_2_4_list = [
            f"nmcli con add type wifi ifname wlan0 mode ap con-name {ap_device_name} ssid {self._ap_wifi_name }",
            f"nmcli con modify {ap_device_name} 802-11-wireless.band bg",
            f"nmcli con modify {ap_device_name} 802-11-wireless.channel 10",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.key-mgmt wpa-psk",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.proto rsn",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.group ccmp",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.pairwise ccmp",
            f"nmcli con modify {ap_device_name} 802-11-wireless-security.psk 12341234",
            f"nmcli con modify {ap_device_name} ipv4.addresses 192.168.109.1/24",
            f"nmcli con modify {ap_device_name} ipv4.gateway 192.168.109.1",
            f"nmcli con modify {ap_device_name} ipv4.method shared",
            f"nmcli con up {ap_device_name}"
        ]
        command_list = command_2_4_list

        for command in command_list:
            print(f"exec: {command}")
            ret,_ = self.cmd_exec.run(command,use_sudo=True)
            if ret != 0:
                print("command exec failed")
                return False,""
        return True, self._ap_wifi_name 

    def connect_wifi(self,ssid,password=None):
        wifi_mode = self.get_current_mode()
        if wifi_mode == "ap":
            self.clear_all_wifi_connect()
            import time
            time.sleep(5) # 两秒不够
        self.wifi_rescan()
        if password is not None:
            command = f"nmcli device wifi connect {ssid} password {password}"
        else:
            command = f"nmcli device wifi connect {ssid}"
        try:
            ret,result = self.cmd_exec.run(command,use_sudo=True)
            connect_info = result
            
            if "successfully" in connect_info:
                print("Connected to WiFi")
                return True
            else:
                print(f"Error connecting to WiFi: {connect_info}")
                if(wifi_mode == "ap"):
                    print("Back to AP mode")
                    self.start_ap_mode()
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to WiFi: {e}")
            self.start_ap_mode()
            return False
    def _scan_wifi_iwlist(self):
        try:
            command = f"iwlist {self._wifi_device} scan"
            ret,result = self.cmd_exec.run(command,use_sudo=True)
            # print(result)
            if ret != 0:
                print("Error scanning Wi-Fi:", result)
                return []
            res_parse = self.parse_wifi_output(result)
            print(res_parse)
            return res_parse
        except subprocess.CalledProcessError as e:
            print(f"Error scanning WiFi: {e}")
            return []
    def _scan_wifi_nmcli(self):
        try:
            command = f"nmcli -t -f SSID,SIGNAL,CHAN,ACTIVE,SECURITY dev wifi"
            ret,result = self.cmd_exec.run(command,use_sudo=True)
            wifi_info = result.split('\n')
            wifi_list = []
            for info in wifi_info:
                parts = info.split(':')
                if len(parts) > 4 and parts[0] != '' and parts[1] != '':
                    ssid, signal, channel, active, security = parts
                    wifi_list.append({
                        'ssid': ssid,
                        'signal': signal,
                        'channel': channel,
                        'active': active,
                        'security': security
                    })     
            print(wifi_list)
            return wifi_list
        except subprocess.CalledProcessError as e:
            print(f"Error scanning WiFi: {e}")
            return []
    def down_ap_role(self):
        print("Down AP Role")
        mode = self.get_current_mode()
        if mode == "ap":
            command = f"nmcli connection down {self._ap_name}"
            ret,result = self.cmd_exec.run(command,use_sudo=True)
            if ret == 0:
                print("AP Role down successfully")
                return True
            else:
                print(f"Failed to down AP Role: {result}")
                return False
        else:
            print("Not in AP mode, no need to down")
            return True
    def reup_ap_role(self):
        print("Reup AP Role")
        mode = self.get_current_mode()
        if mode == "ap":
            command = f"nmcli connection up {self._ap_name}"
            ret,result = self.cmd_exec.run(command,use_sudo=True)
            if ret == 0:
                print("AP Role reup successfully")
                return True
            else:
                print(f"Failed to reup AP Role: {result}")
                return False
        else:
            print("Not in AP mode, no need to reup")
            return True
    def scan_wifi(self):
        print("Scanning WiFi")
        mode = self.get_current_mode()
        if mode == "ap":
            print("In AP mode, can't connect to wifi")
            # self.down_ap_role()
            result = self._scan_wifi_iwlist()
            # self.reup_ap_role()
            return result
        elif mode == "sta":
            print("In STA mode")
            return self._scan_wifi_nmcli()

if __name__ == "__main__":
    auth = Auth()
    print(auth.verify_token("emnavi","123456"))
    network_control = NetworkControl(auth)
    # network_control.clear_all_wifi_connect()
    # network_control.start_ap_mode()
    network_control.connect_wifi("mix-alpha","123456789")
    print(network_control.get_current_mode())