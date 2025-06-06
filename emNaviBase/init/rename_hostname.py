# 命名规则
import random
import string
import argparse
import os
import sys
import socket

def is_root(): 
	return os.geteuid() == 0
# 在生成主机名之后，设置主机名
def set_hostname(hostname):
    current_hostname = socket.gethostname()
    os.system(f"sudo hostnamectl set-hostname {hostname}")
    # 更新 /etc/hosts 文件
    update_etc_hosts(current_hostname, hostname)

def update_etc_hosts(old_hostname, new_hostname):
    hosts_file = '/etc/hosts'
    
    # 读取 /etc/hosts 内容
    with open(hosts_file, 'r') as file:
        lines = file.readlines()
    
    # 查找并替换旧的主机名为新的主机名
    new_lines = []
    for line in lines:
        # 替换所有出现的旧主机名
        new_lines.append(line.replace(old_hostname, new_hostname))
    
    # 以写入模式重新写入文件
    with open(hosts_file, 'w') as file:
        file.writelines(new_lines)




# 生成随机后缀
def generate_random_suffix(length=4):
    characters = string.ascii_letters + string.digits  # 包含字母和数字
    suffix = ''.join(random.choice(characters) for _ in range(length))
    return suffix

# 生成主机名
def generate_hostname(prefix, drone_type, custom_id):
    if not prefix:
        prefix = "emNavi"  # 如果没有提供前缀，则使用默认值
    random_suffix = generate_random_suffix()
    hostname = f"{prefix}-{drone_type}-{custom_id}-{random_suffix}"
    return hostname

if __name__ == "__main__": 
    if not is_root(): 
        print("该脚本需要以 root 权限执行。请使用 sudo 运行。") 
        sys.exit(1)

    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="生成无人机主机名")
    parser.add_argument("--prefix", type=str, help="前缀(默认为 'emNavi')")
    parser.add_argument("--drone_type", type=str, required=True, help="无人机类型")
    parser.add_argument("--custom_id", type=str, required=True, help="ID")

    # 解析命令行参数
    args = parser.parse_args()

    # 生成并打印主机名
    hostname = generate_hostname(args.prefix, args.drone_type, args.custom_id)
    print(f"生成的主机名: {hostname}")
    # set hostname 
    # 设置系统主机名 
    set_hostname(hostname)