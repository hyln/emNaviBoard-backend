from emNaviBase.utils.network_control import NetworkControl
import threading
import time



class WifiHijackManager:
    def __init__(self):
        self.nc = NetworkControl("root","123")

    def start_hijack_monitor(self):

        def monitor():
            end_time = time.time() + 60  # Run for 1 minute
            while time.time() < end_time:
                self.nc.wifi_rescan()
                time.sleep(1)
                available_networks = self.nc.scan_wifi()
                for network in available_networks:
                    if network['ssid'] == 'emNaviHijack':
                        self.nc.connect_wifi('emNaviHijack', '12341234')
                        return
                time.sleep(10)  # Check every 5 seconds

        threading.Thread(target=monitor, daemon=True).start()