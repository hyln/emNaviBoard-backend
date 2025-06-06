#!/usr/bin/env python3

import os
import sys
import pwd
import subprocess

USERNAME = "root"
NEW_PASSWORD = "emNavi"

# 1. 检查是否以 root 身份运行
if os.geteuid() != 0:
    print("Error: This script must be run as root.")
    sys.exit(1)

# 2. 检查用户是否存在
try:
    pwd.getpwnam(USERNAME)
except KeyError:
    print(f"Error: User '{USERNAME}' does not exist.")
    sys.exit(1)

# 3. 修改密码
try:
    # 传入格式为 "user:password"
    subprocess.run(
        ["chpasswd"],
        input=f"{USERNAME}:{NEW_PASSWORD}".encode("utf-8"),
        check=True,
    )
    print(f"用户 '{USERNAME}' 的密码已重置为 '{NEW_PASSWORD}'.")
except subprocess.CalledProcessError:
    print("重置密码失败")
    sys.exit(1)
