
import subprocess
from auth import Auth
class NetworkControl():
    def __init__(self,auth:Auth) -> None:
        self._auth = auth
    def set_auth(self,auth:Auth):
        self._auth = auth
    def clear_all_wifi_connect(self):
        if not self._auth.isLogin():
            print("Not login")
            return False
        try:
            command = f"echo {self._auth['password']} | sudo -S nmcli -t -f NAME,TYPE connection show"
            result = subprocess.run(command, capture_output=True, text=True) # Get the list of all Wi-Fi connections
            connections = result.stdout.strip().split('\n')

            # Delete each Wi-Fi connection
            for connection in connections:
                name, conn_type = connection.split(':')
                if conn_type == '802-11-wireless':  # Ensure the connection type is Wi-Fi
                    subprocess.run(['nmcli', 'connection', 'delete', name])
                    print(f"Deleted Wi-Fi connection: {name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def start_ap_mode(self):
        ap_device_name= "wifi_ap"
        # get hostname
        host_name = subprocess.run("hostname", stdout=subprocess.PIPE).stdout.decode("utf-8").strip()
        ap_name = host_name+"_"+"5G"
        # 检测是否已经存在该连接
        cmd_check_connection = f"echo {self._auth['password']} | sudo -S nmcli connection show | grep {ap_device_name}"
        completedProc = subprocess.run(cmd_check_connection, shell=True)
        if completedProc.returncode == 0:
            print(f"connection {ap_device_name}  already exists")      
            cmd_delete_connection = f"nmcli connection delete {ap_device_name}"
            completedProc = subprocess.run(cmd_delete_connection, shell=True)
            if completedProc.returncode != 0:
                print("connection delete failed")
                return False
        command_list = [
            f"echo {self._auth['password']} | sudo -S nmcli con add type wifi ifname wlan0 mode ap con-name {ap_device_name} ssid {ap_name}",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless.band a",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless.channel 149",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless-security.key-mgmt wpa-psk",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless-security.proto rsn",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless-security.group ccmp",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless-security.pairwise ccmp",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} 802-11-wireless-security.psk 12341234",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} ipv4.addresses 192.168.109.1/24",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} ipv4.gateway 192.168.109.1",
            f"echo {self._auth['password']} | sudo -S nmcli con modify {ap_device_name} ipv4.method shared",
            f"echo {self._auth['password']} | sudo -S nmcli con up {ap_device_name}"
        ]
        for command in command_list:
            print(f"exec: {command}")
            completedProc = subprocess.run(command, shell=True)
            if completedProc.returncode != 0:
                print("command exec failed")
                return False
        return ap_name

    def connect_wifi(self,ssid,password=None):
        if password is not None:
            command = f"echo {self._auth['password']} | sudo -S nmcli dev wifi connect {ssid} password {password}"
        else:
            command = f"echo {self._auth['password']} | sudo -S nmcli dev wifi connect {ssid}"
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                print("Connected to WiFi")
                return True
            else:
                print(f"Error connecting to WiFi: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to WiFi: {e}")
            return False
    def scan_wifi(self):
        print("Scanning WiFi")
        try:
            command = f"echo {self._auth["password"]} | sudo -S nmcli -t -f SSID,SIGNAL,CHAN,ACTIVE,SECURITY dev wifi"
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