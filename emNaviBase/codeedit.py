import sys
import requests

def send_file_to_server(file_path):
    url = 'http://127.0.0.1:5000/codeedit/upload'
    files_path = {'file_path': file_path}        
    response = requests.post(url, files=files_path)
    return response

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python codeedit.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    response = send_file_to_server(file_path)
    print(f"Server response: {response.text}")