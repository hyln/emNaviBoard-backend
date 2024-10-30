
import subprocess
import re
from .auth import Auth
class NetworkControl():
    def __init__(self,auth) -> None:
        self._token = auth.token
        self._sudo_prefix = f"echo {self._token['password']} | sudo -S "

        host_name = subprocess.run("hostname", stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
        self._ap_wifi_name = host_name+"_"+"5G"
        self._wifi_device = "wlan0"
        self._ap_name = "wifi_ap"
        print(self._sudo_prefix )

    def set_auth(self,auth:Auth):
        self._token = auth.token
        self._sudo_prefix = f"echo {self._token['password']} | sudo -S "
        print(self._sudo_prefix )

    def parse_wifi_output(self,output):
        wifi_info = []
        
        # 使用正则表达式匹配 Cell 信息
        cells = output.strip().split('Cell ')
        for cell in cells[1:]:  # 跳过第一个元素
            ssid_match = re.search(r'ESSID:"(.+?)"', cell)
            signal_match = re.search(r'Signal level:(-?\d+) dBm', cell)
            freq_match = re.search(r'Frequency[=: ]([\d.]+) GHz \(Channel (\d+)\)', cell)
            key_match = re.search(r'Encryption key:(\w+)', cell)
            
            # 提取安全性信息
            security_match = re.search(r'IE: (.+?)\n', cell)
            security = None
            if security_match:
                # 查找 WPA 或 WPA2
                if 'WPA2' in security_match.group(1):
                    security = 'WPA2'
                elif 'WPA3' in security_match.group(1):
                    security = 'WPA3'
                elif 'WPA' in security_match.group(1):
                    security = 'WPA'
                else:
                    security = 'None'

            if ssid_match and signal_match and freq_match and key_match:
                ssid = ssid_match.group(1)
                signal = signal_match.group(1) + ' dBm'
                channel = freq_match.group(2)
                # active = 'yes' if key_match.group(1) == 'on' else 'no'
                active = 'no'

                wifi_info.append({
                    'ssid': ssid,
                    'signal': signal,
                    'channel': channel,
                    'active': active,
                    'security': security
                })

        return wifi_info
    def get_ap_wifi_name(self):
        return self._ap_wifi_name
    def get_current_mode(self):
        try:
            command = self._sudo_prefix + "nmcli -t -f NAME,TYPE connection show"
            print(command)
            result = subprocess.run(command,shell=True, capture_output=True, text=True) # Get the list of all Wi-Fi connections
            connections = result.stdout.strip()
            if(self._ap_name in connections):
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
            command = self._sudo_prefix + "nmcli device wifi rescan"
            result = subprocess.run(command,shell=True, capture_output=True, text=True)
            print("Rescanning Wi-Fi")
            return True
    
    def clear_all_wifi_connect(self):
        try:
            command = self._sudo_prefix + "nmcli -t -f NAME,TYPE connection show"
            result = subprocess.run(command,shell=True, capture_output=True, text=True) # Get the list of all Wi-Fi connections
            connections = result.stdout.strip().split('\n')

            # Delete each Wi-Fi connection
            for connection in connections:
                name, conn_type = connection.split(':')
                if conn_type == '802-11-wireless':  # Ensure the connection type is Wi-Fi
                    command = self._sudo_prefix + f"nmcli connection delete {name}"
                    result = subprocess.run(command,shell=True, capture_output=True, text=True) # Get the list of all Wi-Fi connections
                    print(f"Deleted Wi-Fi connection: {name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def start_ap_mode(self):
        ap_device_name= self._ap_name
        # 检测是否已经存在该连接
        cmd_check_connection = self._sudo_prefix + f"nmcli connection show | grep {ap_device_name}"
        completedProc = subprocess.run(cmd_check_connection, shell=True)
        if completedProc.returncode == 0:
            print(f"connection {ap_device_name}  already exists")      
            cmd_delete_connection = f"echo {self._token['password']} | sudo -S nmcli connection delete {ap_device_name}"
            completedProc = subprocess.run(cmd_delete_connection, shell=True)
            if completedProc.returncode != 0:
                print("connection delete failed")
                return False
        command_list = [
            self._sudo_prefix + f"nmcli con add type wifi ifname wlan0 mode ap con-name {ap_device_name} ssid {self._ap_wifi_name }",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless.band a",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless.channel 149",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless-security.key-mgmt wpa-psk",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless-security.proto rsn",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless-security.group ccmp",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless-security.pairwise ccmp",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} 802-11-wireless-security.psk 12341234",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} ipv4.addresses 192.168.109.1/24",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} ipv4.gateway 192.168.109.1",
            self._sudo_prefix + f"nmcli con modify {ap_device_name} ipv4.method shared",
            self._sudo_prefix + f"nmcli con up {ap_device_name}"
        ]
        for command in command_list:
            print(f"exec: {command}")
            completedProc = subprocess.run(command, shell=True)
            if completedProc.returncode != 0:
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
            command = self._sudo_prefix + f"nmcli device wifi connect {ssid} password {password}"
        else:
            command = self._sudo_prefix + f"nmcli device wifi connect {ssid}"
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            connect_info = result.stdout.strip()
            
            if "successfully" in connect_info:
                print("Connected to WiFi")
                return True
            else:
                print(f"Error connecting to WiFi: {result.stderr}")
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
            command = self._sudo_prefix + f"iwlist {self._wifi_device} scan"
            result = subprocess.run(command, shell=True, text=True, capture_output=True) # shell=true 一定要有
            print(result.stdout)
            if result.returncode != 0:
                print("Error scanning Wi-Fi:", result.stderr)
                return []
            return self.parse_wifi_output(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error scanning WiFi: {e}")
            return []
    def _scan_wifi_nmcli(self):
        try:
            command = self._sudo_prefix + f"nmcli -t -f SSID,SIGNAL,CHAN,ACTIVE,SECURITY dev wifi"
            result = subprocess.run(command, shell=True, text=True, capture_output=True) # shell=true 一定要有
            wifi_info = result.stdout.strip().split('\n')
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
    def scan_wifi(self):
        print("Scanning WiFi")
        mode = self.get_current_mode()
        if mode == "ap":
            print("In AP mode, can't connect to wifi")
            return self._scan_wifi_iwlist()
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