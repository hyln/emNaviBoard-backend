from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
from utils.auth import Auth
from utils.network_control import NetworkControl
app = Flask(__name__)
CORS(app)  # 允许所有来源的请求

auth = Auth()
network_control = NetworkControl(auth)
 
 
@app.route('/api/get-ap-wifi-name', methods=['GET'])
def get_ap_wifi_name():
    return jsonify({'ap_wifi_name': network_control.get_ap_wifi_name()})
@app.route('/api/set-ap-mode', methods=['GET'])
def set_ap_mode():
    ret,ap_wifi_name=network_control.start_ap_mode()
    if ret:
        return jsonify({'status': 'success', 'ap_wifi_name': ap_wifi_name})
    else:
        return jsonify({'status': 'error', 'ap_wifi_name': ''}), 500

@app.route('/api/get-wifi-mode', methods=['GET'])
def get_wifi_mode():
    return jsonify({'mode': network_control.get_current_mode()})

@app.route('/api/wifi', methods=['GET'])
def get_wifi_list():
    wifi_list = network_control.scan_wifi()
    return jsonify(wifi_list)

@app.route('/api/connect', methods=['POST'])
def connect_wifi():
    data = request.json
    print(data)
    ssid = data.get('ssid')
    wifi_password = data.get('password')
    print(f"Connecting to WiFi: {ssid}")
    if not ssid:
        return jsonify({'status': 'error', 'message': 'SSID is required.'}), 400

    try:
        ret = False
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

@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    print("Received request")

    data = request.json
    username = data.get('username')
    password = data.get('password')
    auth.verify_token(username,password)
    if auth.isLogin():
        network_control.set_auth(auth)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'}), 200

if __name__ == '__main__':
    app.run(port=5000,host="0.0.0.0")
