from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
from typing import List
import socket
from flask_socketio import SocketIO, emit
import shortuuid
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from emNaviBase.utils.auth import Auth
from emNaviBase.utils.network_control import NetworkControl
from emNaviBase.utils.proxy_control import ProxyControl
from emNaviBase.utils.self_discover import SelfDiscover
from emNaviBase.utils.wifi_hijack import WifiHijackManager
from emNaviBase.utils.ttyd_manager import TTYDManager
app = Flask(__name__)
CORS(app)  # 允许所有来源的请求
# app.secret_key = 'your_secret_key'

# socketio = SocketIO(app, cors_allowed_origins="*")
# 注意CORS(app) 并不能帮SocketIO 解决cors问题 需要cors_allowed_origins="*"

auths:List[Auth] = []
ttyd_manager = TTYDManager()

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
 
#  登录
@app.route('/api/verify_login', methods=['GET'])
def verify_login():
    # 检查是否登录
    device_id = request.args.get('device_id')
    session_id = shortuuid.uuid()[:15]


    for i in auths:
        if i.get_device_id() == device_id:
            username = i.get_username()
            ttyd_index = ttyd_manager.get_ttyd_index(username)
            ttyd_uuid = ttyd_manager.get_ttyd_uuid(username)
            return jsonify({'status': 'success',"session_id": session_id,"ttyd_index": ttyd_index,"ttyd_uuid": ttyd_uuid}), 200
    return jsonify({'status': 'failure',"session_id": session_id}), 200
@app.route('/api/login', methods=['POST'])
def login():
    print("Received request")
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # 删除掉过去的登录信息
    # 运行同时登录，删除大于一天的登录信息
    # 用户量非常少，不考虑更多问题
    for i in auths:
        if i.is_timeout():
            auths.remove(i)
    # 登录
    auth = Auth(username,password)
    ret,device_id,session_id =auth.verify_token()
    if ret:
        auths.append(auth)
        # 由于不使用数据库，所以登录时启动ttyd即可
        username = auth.get_username()
        password = auth.get_password()
        ttyd_index = ttyd_manager.get_ttyd_index(username)
        ttyd_uuid = ttyd_manager.get_ttyd_uuid(username)
        # ttyd_port = 7681
        # if(not is_port_in_use(ttyd_port)):
            # TODO: 根据不同用户启动不同的ttyd
            # proc = subprocess.Popen(f'sudo -u {username} /opt/emnaviboard/pkg/ttyd -p {ttyd_port} -b /ttyd/ -W bash', shell=True)
            # proc.wait()
            # subprocess.Popen(f'export TTYD_SESSION=true;cd ~ ; ttyd -p {ttyd_port} -b /ttyd/ -W bash', shell=True)
            # print("TTYD started.")
        return jsonify({'status': 'success', 'device_id': device_id,"session_id": session_id,"ttyd_index": ttyd_index,"ttyd_uuid": ttyd_uuid}), 200
    else:
        return jsonify({'status': 'failure'}), 200
@app.route('/api/getttyd', methods=['GET'])
def open_ttyd():
    device_id = request.args.get('device_id')
    for i in auths:
        if i.get_device_id() == device_id:
            ttyd_index = ttyd_manager.get_ttyd_index(i.get_username())
            ttyd_uuid = ttyd_manager.get_ttyd_uuid(i.get_username())
            if ttyd_index:
                return jsonify({'status': 'success', 'ttyd_index': ttyd_index,"ttyd_uuid": ttyd_uuid}), 200
            else:
                return jsonify({'status': 'error', 'message': 'TTYD not found'}), 404
    return jsonify({'status': 'error', 'message': 'User not found'}), 404

@app.route('/api/logout', methods=['POST'])
def logout():
    data = request.json
    device_id = data.get('device_id')
    for i in auths:
        if i.get_device_id() == device_id:
            auths.remove(i)
            return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 500

# 网络管理
@app.route('/api/get-ap-wifi-name', methods=['GET'])
def get_ap_wifi_name():
    device_id = request.args.get('device_id')  # 获取 device_id 参数
    for i in auths:
        if i.get_device_id() == device_id:
            pass
            # TODO： Orin 不能使用AP模式，因此删掉
            # network_control = NetworkControl(i.get_username(),i.get_password())
            # return jsonify({'status': 'success', 'ap_wifi_name': network_control.get_ap_wifi_name()})
    return jsonify({'status': 'error', 'ap_wifi_name': ''})
@app.route('/api/set-ap-mode', methods=['GET'])
def set_ap_mode():
    device_id = request.args.get('device_id')  # 获取 device_id 参数
    for i in auths:
        if i.get_device_id() == device_id:
            network_control = NetworkControl(i.get_username(),i.get_password())
            ret,ap_wifi_name=network_control.start_ap_mode()
            if ret:
                return jsonify({'status': 'success', 'ap_wifi_name': ap_wifi_name})
            else:
                return jsonify({'status': 'error', 'ap_wifi_name': ''}), 500

@app.route('/api/get-wifi-mode', methods=['GET'])
def get_wifi_mode():
    device_id = request.args.get('device_id')  # 获取 device_id 参数
    for i in auths:
        if i.get_device_id() == device_id:
            network_control = NetworkControl(i.get_username(),i.get_password())
            mode=network_control.get_current_mode()
            return jsonify({'status': 'success', 'mode': mode})
    return jsonify({'status': 'error', 'mode': ''}), 500

@app.route('/api/wifi', methods=['GET'])
def get_wifi_list():
    device_id = request.args.get('device_id')  # 获取 device_id 参数
    for i in auths:
        if i.get_device_id() == device_id:
            network_control = NetworkControl(i.get_username(),i.get_password())
            wifi_list = network_control.scan_wifi()
            return jsonify(wifi_list)
    return jsonify({'status': 'error'}), 500

@app.route('/api/connect', methods=['POST'])
def connect_wifi():
    # 判断是否登录
    device_id = request.json.get('device_id')
    print(device_id)
    is_login = False
    auth = None
    for i in auths:
        if i.get_device_id() == device_id:
            is_login = True
            auth = i
            break
    if not is_login:
        return jsonify({'status': 'error', 'message': 'Please login first.'}), 401
    else:
        data = request.json
        print(data)
        ssid = data.get('ssid')
        wifi_password = data.get('password')
        print(f"Connecting to WiFi: {ssid}")
        if not ssid:
            return jsonify({'status': 'error', 'message': 'SSID is required.'}), 400
        try:
            ret = False
            network_control = NetworkControl(auth.get_username(),auth.get_password())
            if(wifi_password != ""):
                ret = network_control.connect_wifi(ssid,wifi_password)
            else:
                ret = network_control.connect_wifi(ssid)
            if ret:
                return jsonify({'status': 'success', 'message': 'Connected to WiFi.'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to connect to WiFi.'}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

# 代理控制
@app.route('/api/get-proxy', methods=['GET'])
def get_proxy():
    # 判断是否登录
    device_id = request.args.get('device_id')
    for i in auths:
        if i.get_device_id() == device_id:
            proxy_control = ProxyControl(i.get_username(),i.get_password()) 
            proxy_status,addr = proxy_control.get_proxy_status()
            return jsonify({'status': 'success', 'proxy_status': proxy_status,'proxy_addr':addr})
    return jsonify({'status': 'error', 'proxy_status': '','proxy_addr': ""}), 500
## 设置代理
@app.route('/api/set-proxy', methods=['POST'])
def set_proxy():
    # 判断是否登录
    device_id = request.json.get('device_id')
    for i in auths:
        if i.get_device_id() == device_id:
            data = request.json
            enable_proxy = data.get('enable_proxy')
            host = data.get('host')
            port = data.get('port')
            proxy_control = ProxyControl(i.get_username(),i.get_password()) 
            proxy_control.set_proxy(enable_proxy,host,port)
            return jsonify({'status': 'success', 'message': 'Proxy set successfully.'})
    return jsonify({'status': 'error', 'message': 'Proxy set failed.'}), 500
# codeedit
@app.route('/codeedit/upload', methods=['POST'])
def upload():
    file_path = request.files['file_path']
    # file_path.save('code.py')
    return jsonify({'status': 'success', 'message': 'File uploaded successfully'}), 200
# 使用webhook通讯文件流

# 启动ttyd
# @app.route('/api/start-ttyd', methods=['GET'])
# def start_ttyd():
#     device_id = request.args.get('device_id')
#     for i in auths:
#         if i.get_device_id() == device_id:
#             username = i.get_username()
#             password = i.get_password()
#             subprocess.Popen(f'ttyd -p 5001 -W bash', shell=True)
#             return jsonify({'status': 'success', 'message': 'TTYD started.'}), 200
#     return jsonify({'status': 'error', 'message': 'Failed to start TTYD.'}), 500
# codeedit
@app.route('/api/file-open', methods=['POST'])
def file_open():
    # 判断是否登录
    device_id = request.json.get('device_id')
    file_path = request.json.get('file_path') 
    session_id = request.json.get('session_id')
    for i in auths:
        if i.get_device_id() == device_id:
            data = request.json
            enable_proxy = data.get('enable_proxy')
            host = data.get('host')
            port = data.get('port')
            proxy_control = ProxyControl(i.get_username(),i.get_password()) 
            proxy_control.set_proxy(enable_proxy,host,port)
            return jsonify({'status': 'success', 'message': 'Proxy set successfully.'})
    return jsonify({'status': 'error', 'message': 'Proxy set failed.'}), 500


# @socketio.on('savefile')
# def handle_message(msg):
#     print('Message received: ' + msg)
#     emit('response', 'Received: ' + msg, broadcast=True)

if __name__ == '__main__':
    ttyd_manager.start_ttyd_for_all_users()

    self_discover = SelfDiscover()
    wifi_hijack = WifiHijackManager()
    wifi_hijack.start_hijack_monitor()
    # 部署时通过nginx转发,不需要设置host
    # app.run(port=5000,host="127.0.0.1")
    app.run(port=4630,host="0.0.0.0")
    # socketio.run(app, port=5000,host="0.0.0.0")
