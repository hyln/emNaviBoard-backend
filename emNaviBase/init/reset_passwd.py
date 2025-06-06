#!/usr/bin/env python3

import os
import sys
import pwd
import subprocess

def main():
    if os.geteuid() != 0:
        print("Error: This script must be run as root.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: sudo python3 -m emNaviBase.init.reset_passwd 用户名 [新密码]")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2] if len(sys.argv) >= 3 else "123456"

    # 检查用户是否存在
    try:
        pwd.getpwnam(username)
    except KeyError:
        print(f"Error: 用户 '{username}' 不存在.")
        sys.exit(1)

    # 修改密码
    try:
        subprocess.run(
            ["chpasswd"],
            input=f"{username}:{new_password}",
            text=True,
            check=True
        )
        print(f"用户 '{username}' 的密码已重置为 '{new_password}'.")
    except subprocess.CalledProcessError:
        print("重置密码失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
