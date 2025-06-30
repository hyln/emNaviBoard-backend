from emNaviBase.utils.network_control import NetworkControl
import threading
import time



class WifiHijackManager:
    def __init__(self):
        self.nc = NetworkControl("root","123")

    def start_hijack_monitor(self):

        def monitor():
            end_time = time.time() + 60  # Run for 1 minute
            print("WifiHijack Start")
            while time.time() < end_time:
                self.nc.wifi_rescan()
                time.sleep(1)
                available_networks = self.nc.scan_wifi()
                for network in available_networks:
                    if network['ssid'] == 'emNaviHijack':
                        # 如果发现有emNaviHijack的wifi，说明是开机后第一次连接
                        self.nc.connect_wifi('emNaviHijack', '12341234')  # 连接到emNaviHijack
                        # 由于手机 不一定支持广播，所以这里直接开启AP模式
                        # self.nc.start_ap_mode()
                        return # 只在开机后进行1分钟，切换后也马上退出，方便连接其他wifi
                time.sleep(20)  # Check every 5 seconds
            print("WifiHijack exit")

        threading.Thread(target=monitor, daemon=True).start()