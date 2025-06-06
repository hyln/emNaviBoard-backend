# emNaviBoard Backend
## Introduction

> 请使用[emnaviBoard](https://github.com/hyln/emnaviBoard.git) 配置

emNaviBoard Backend 是emNavi 设备工具集的后端，最初使用tauri框架构建，过程中发现rust的语法开发过于困难不适合后续维护，因此使用electron重写了。


## Features

emNaviBoard，为机载电脑提供基础的快速访问功能，
- 网页用户登录
- 集成ttyd，提供基于网页的ssh访问
- 快速在网页端进行wifi操作
- 可通过在记载电脑附近设置一个wifi命名为 emNaviHijack 诱导 记载电脑wifi进入AP模式
- 可快速设置

## 部署
### 安装

为了在目标设备部署emNaviBase，你需要

```bash
git clone https://github.com/yourusername/emNaviBoard-backend.git  # 目前是私有仓库
cd emNaviBoard-backend
# 请务必退出conda，你可以使用 conda deactivate
sudo apt install python3 python3-pip
sudo pip3 install -r requirements.txt

sudo pip install .
```

### 开机自启动



```bash
sudo vim /etc/systemd/system/emNaviBase.service
```

```
[Unit]
Description=emNaviBase
After=network.target
Wants=network.target

[Service]
ExecStart= /usr/bin/python3 -m emNaviBase.run
WorkingDirectory=/home/emnavi
StandardOutput=inherit
StandardError=inherit
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable emNaviBase.service 
systemctl restart emNaviBase.service 
```

### 配置前端界面

```
https://github.com/hyln/emnaviBoard
```


## 端口占用

- ttyd: 7681
- selfDiscover:  21245, 21246
- emNaviBase: 5000


## 初始化脚本


```bash
source /opt/emnaviboard/emnvboard-env/bin/activate
# 重置root的密码为 emNavi
sudo python -m emNaviBase.init.reset_default_root_passwd
# 清除缓存，制作系统快照前使用
sudo python -m emNaviBase.init.clean_cache
# 设置hostname
sudo python -m emNaviBase.init.rename_hostname --prefix emNavi --drone_type X280 --custom_id 1
# 修改用户名
sudo python -m emNaviBase.init.rename_username 

# 重置密码
sudo python -m emNaviBase.init.reset_passwd emnavi 123456


```

> 

<!-- 
## Todo
### emcode

为了上emcode仅在ttyd的环境中生效，需要在 `/etc/bash.bashrc` 的末尾增加
```bash
if [[ "$TTYD_SESSION" == "true" ]]; then
    alias emcode='run emcode'
fi
```

### ttyd 
使用 7681 端口 
 -->


