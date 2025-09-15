import threading
import time
import socket
import json
import netifaces
from getmac import get_mac_address
import struct
import random


class SelfDiscover():
    def __init__(self, device_name: str ="", listen_port: int = 21245,send_port: int = 21246, broadcast_min_interval: int = 3):
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

        MCAST_GRP = '224.0.0.1'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.listen_port))  # 注意这里绑定 ''，不是具体的 IP

        for i in range(10):
            try:
                # 加入多播组
                mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                print("Multicast group joined successfully.")
                break
            except OSError as e:
                print(f"Attempt {i+1}: Multicast join failed, retrying in 1s... ({e})")
                time.sleep(1)

        self.broadcast_thread = threading.Thread(target=self.listen_for_trigger, daemon=True)
        self.broadcast_thread.start()
        print("Self Discover start")
        threading.Thread(target=self.broadcast).start()

    def listen_for_trigger(self):
        print("Listening for discovery requests...")
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
                time.sleep(self.broadcast_min_interval + random.uniform(0, 1))
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