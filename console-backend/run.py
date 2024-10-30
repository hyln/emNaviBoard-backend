from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS
import pexpect
from utils.auth import Auth
from utils.network_control import NetworkControl
app = Flask(__name__)
CORS(app)  # 允许所有来源的请求

auth = Auth()
 


@app.route('/api/wifi', methods=['GET'])
def get_wifi_list():
    wifi_list = scan_wifi()
    return jsonify(wifi_list)

@app.route('/api/connect', methods=['POST'])
def connect_wifi():
    data = request.json
    ssid = data.get('ssid')

    if not ssid:
        return jsonify({'status': 'error', 'message': 'SSID is required.'}), 400

    try:
        # 连接到 WiFi
        # 这里假设你已经有相应的密码和连接逻辑
        subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid], check=True)
        return jsonify({'status': 'success', 'message': 'Connected to WiFi.'})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    print("Received request")
    print("###############")

    data = request.json
    print(data)
    print("###############")
    username = data.get('username')
    password = data.get('password')
    auth.verify_token(username,password)
    if auth.isLogin():
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'}), 200

if __name__ == '__main__':
    app.run(port=5000)
