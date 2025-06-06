import threading
import time
import socket
import json
from cryptography.fernet import Fernet
import netifaces
import uuid
from getmac import get_mac_address


class SelfDiscover():
    def __init__(self, device_name: str ="", listen_port: int = 21245,send_port: int = 21246, broadcast_min_interval: int = 5):
        # self.message = message
        if device_name == "":
            self.device_name = socket.gethostname()
        else:
            self.device_name = device_name
        mac = get_mac_address()
        self.device_info = {"device_name": self.device_name, "ip_addresses": "" ,"mac":str(mac),"last_updated":int(time.time())}
        self.broadcast_min_interval = broadcast_min_interval
        self.listen_port = listen_port
        self.send_port = send_port
        self.running = False
        self.send_ip = "<broadcast>" # 要是没有的话就是广播
    

        self.discov_req_msg = "EMNAVI_DEV_DISCOV_REQ"

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', self.listen_port))  # 监听所有可用接口
        self.broadcast_thread = threading.Thread(target=self.listen_for_trigger, daemon=True)
        self.broadcast_thread.start()

        threading.Thread(target=self.broadcast).start()

    def listen_for_trigger(self):
        while True:
            data, addr = self.sock.recvfrom(1024)  # 接收数据
            message = data.decode('utf-8')
            print(f"Received message: '{message}' from {addr}")
            if message == self.discov_req_msg:
                print("Triggering broadcast...")
                self.send_ip = addr[0]
                self.running = True
                # self.broadcast_message()
    def stop_broadcasting(self):
        """停止广播消息."""
        self.running = False
    def broadcast(self):
        """定期广播消息."""
        while True:
            if(self.running):
                self.running = False
                self.device_info["ip_addresses"] = self.get_ip_addresses()
                json_message = json.dumps(self.device_info)

                try:
                    self.sock.sendto(json_message.encode('utf-8'), (self.send_ip, self.send_port))
                except OSError as e:
                    print(f"[SelfDiscover] Failed to send broadcast: {e}")                    
                except Exception as e:
                    print(f"[SelfDiscover] Unexpected error: {e}")
                print(f"Broadcasting message: {json_message}")
                time.sleep(self.broadcast_min_interval)
            else:
                time.sleep(0.5)
    def close(self):
        """关闭 UDP 套接字."""
        self.sock.close()
    def get_ip_addresses(self):
        ip_addresses = {}
        for interface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for link in addresses[netifaces.AF_INET]:
                    if( interface != "lo"):
                        ipv4 = link['addr']
                        ip_addresses[interface] = ipv4
        return ip_addresses

if __name__ == "__main__":
    hostname = socket.gethostname()  # 获取本地主机名
    discover = SelfDiscover(hostname)
    try:
        print("Press Ctrl+C to stop broadcasting...")
        while True:
            time.sleep(1)  # 主线程保持活动
    except KeyboardInterrupt:
        discover.stop_broadcasting()
        discover.close()
        print("Broadcasting stopped.")