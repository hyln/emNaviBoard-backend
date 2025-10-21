import pwd
import subprocess
import shortuuid

class TTYDManager:
    def __init__(self,starting_port: int = 7781):
        self.starting_port = starting_port
        self.ttyd_group = {}
        self.ttyd_uuid_group = {}

    def _find_all_users(self):
        return [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000 and 'nologin' not in user.pw_shell and 'false' not in user.pw_shell]
    def _start_ttyd_for_user(self, username: str, port: int):
        ttyd_uuid = shortuuid.uuid()[:15]

        ttyd_port = port
        proc = subprocess.Popen(f'sudo -u {username} /opt/emnaviboard/pkg/ttyd -c admin:{ttyd_uuid} -p {ttyd_port} -b /ttyd/ -W bash', shell=True)
        self.ttyd_group[username] = ttyd_port
        self.ttyd_uuid_group[username] = ttyd_uuid
        print(f"Started TTYD session for user {username} on port {port}")
        return port
    def start_ttyd_for_all_users(self):
        users = self._find_all_users()
        for i, user in enumerate(users):
            self._start_ttyd_for_user(user, 1+i)
    def get_ttyd_index(self, username: str):
        return self.ttyd_group.get(username, None)
    def get_ttyd_uuid(self, username: str):
        return self.ttyd_uuid_group.get(username, None)

if __name__ == "__main__":
    ttyd_manager = TTYDManager()
    users = ttyd_manager._find_all_users()
    print("System Users:", users)