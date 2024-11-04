# emNaviBoard Backend
## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The emNaviBoard Backend is a RESTful API service designed to manage and serve data for the emNaviBoard application. It is built using modern web technologies and follows best practices for API development.

## Features

emNaviBoard，为机载电脑提供基础功能，
- 用户登录
- 集成ttyd
- 快速网络操作
- 断电遗忘

## 部署

### emcode

为了上emcode仅在ttyd的环境中生效，需要在 `/etc/bash.bashrc` 的末尾增加
```bash
if [[ "$TTYD_SESSION" == "true" ]]; then
    alias emcode='run emcode'
fi
```

### ttyd 
使用 7681 端口 


## Installation

To get started with the emNaviBoard Backend, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/emNaviBoard-backend.git
    cd emNaviBoard-backend
    ```

    ```bash
    sudo pip3 install -r requirements.txt
    sudo pip3 install .
    ```

## 开机自启动

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

