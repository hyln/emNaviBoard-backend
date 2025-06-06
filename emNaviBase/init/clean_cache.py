import os
import subprocess

def clean_cache_root():
    # Clear bash history for root and emnavi
    with open('/root/.bash_history', 'w'):
        pass
    subprocess.run('bash -c "history -c"', shell=True, check=True)
    # Remove temporary files
    subprocess.run(['rm', '-rf', '/tmp/*'], check=True)
    subprocess.run(['rm', '-rf', '/root/.cache/*'], check=True)
    # Remove log files
    subprocess.run(['sudo', 'rm', '-rf', '/var/log/*'], check=True)
    # Vacuum journal logs
    subprocess.run(['journalctl', '--vacuum-time=1d'], check=True)
    # Clean apt cache
    subprocess.run(['apt', 'clean'], check=True)
def clean_cache_user(username):
    # Remove cache directories
    command = f'rm -rf /home/{username}/.cache/'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if(result.returncode == 0):
        print("rm -rf /home/{username}/.cache/")
    command = f'rm /home/{username}/.bash_history'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if(result.returncode == 0):
        print("'rm /home/{username}/.bash_history")
    

if __name__ == "__main__":
    if(os.getuid() == 0):
        clean_cache_root()
        clean_cache_user('emnavi')
    else:
        print("Please run this script as root")
    