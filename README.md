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

2. **Install dependencies:**
    ```bash
    pip install flask
    ```

## Usage

Once the application is running, you can access the API at `http://localhost:5000`. Refer to the API documentation for detailed information on available endpoints and their usage.