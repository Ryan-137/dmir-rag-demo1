# 手工制作一个RAG框架

[学习链接](https://u.geekbang.org/subject/airag/1009927) https://u.geekbang.org/subject/airag/1009927

一个从零开始实现的 RAG (Retrieval Augmented Generation) 系统，不依赖现有的 RAG 框架。该项目旨在提供一个轻量级、可定制的知识库问答解决方案。
![RAG Frontend](images/RAG-fontend.png)

本仓库基于老师提供的 RAG 框架模板精简整理而来，保留核心前后端代码和部署说明，移除了本地依赖、缓存、运行生成结果和无用脚手架，便于后续在课程模板基础上继续迭代。

## 项目概述

本项目是一个完全自主实现的 RAG 系统，通过将文档分块、向量化存储、相似度检索等核心功能模块化实现，使用户能够构建自己的知识库问答系统。

### 核心特性

- 文档分块：支持自定义大小的文档分块策略
- 向量化存储：将文本块转换为向量并高效存储
- 相似度检索：基于向量相似度进行智能匹配
- 无框架依赖：不依赖 LangChain 等重量级 RAG 框架
- 跨平台支持：同时支持 Windows 和 Ubuntu 环境

## 部署安装

### 拉取代码

你可以通过克隆此仓库到你的本地机器来开始：

```shell
git clone https://github.com/answerend42/dmir-rag-demo.git
```

然后导航至目录，并按照部署前端或后端的指示开始操作。

### 部署前端 (Ubuntu) 

#### 1. 检查是否已安装 npm：

- 进入前端项目目录（例如 `cd frontend/`）。
- 在终端中运行命令：`npm -v`
- 如果已安装，将显示 npm 的版本号。

#### 2. 安装 Node.js 和 npm：

- 更新 apt 软件包列表：`sudo apt update`
- 安装 Node.js 和 npm：`sudo apt install nodejs npm -y`
- **备注**：项目中使用的`node`版本为`v22.14.0` ， `npm`版本为`10.9.2`

#### 3. 安装前端组件：

- 运行 `npm install` 命令来安装项目依赖的前端组件。

#### 4. 运行前端组件：

修改`frontend\src\config\config.js`中的代码环境地址`apiBaseUrl`

```bash
const config = {
              development: {
                apiBaseUrl: 'http://192.168.172.128:8001'
              },
              production: {
                apiBaseUrl: 'http://api.example.com'
              },
              test: {
                apiBaseUrl: 'http://localhost:8001'
              }
            };
```

运行 `npm run dev` 命令来安装项目依赖的前端组件。

```bash
# 默认是 development 环境
npm run dev

# 或者指定环境
npm run dev -- --mode production
```

### 部署前端 (MacOS)
- **备注**：项目中使用的`node`版本为`v22.14.0` ， `npm`版本为`10.9.2`
#### 1. 安装 Node.js

```shell
# 1. 安装Homebrew（若未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 更新Homebrew
brew update

# 3. 安装Node.js（含npm）
brew install node

# 4. 验证安装
node -v  # 输出Node.js版本号
npm -v   # 输出npm版本号
```

#### 2. 安装前端依赖并启动

```shell
# 进入前端项目目录并安装依赖
cd frontend && npm install

# 如果提示vite未安装，执行以下命令
npm install vite

# 启动项目
npm run dev
```

### 部署后端 (Ubuntu/MacOS) 

本项目原始版本使用 Python v3.10 开发；当前项目推荐使用 `uv` 管理 Python 环境和依赖，已在 Python `3.14.4` 下完成基础启动验证。

- Windows 环境： [requirements_win.txt](https://github.com/huangjia2019/rag-project01-framework/blob/master/requirements_win.txt)
  - 由于Windows不支持Milvus数据库，可以采用docker安装Milvus数据库或者更换为Chroma(本项目有个佳哥的Chroma分支)

- Ubuntu 环境： [requirements_ubun.txt](https://github.com/huangjia2019/rag-project01-framework/blob/master/requirements_ubun.txt)

关键依赖的官方文档如下：

- Python 环境管理 [uv](https://docs.astral.sh/uv/)
- 备用方案：[Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)

#### 1. 安装 uv

```shell
# MacOS
brew install uv

# Ubuntu / Linux / Windows 可参考 uv 官方安装方式
# https://docs.astral.sh/uv/getting-started/installation/
```

国内环境建议使用清华 PyPI 镜像源：

```shell
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. 创建 Python 3.14 环境

在项目根目录执行：

```shell
uv venv --python 3.14
source .venv/bin/activate
python -V
```

如果本机没有 Python 3.14，`uv` 会自动下载可用版本；也可以先查看可用版本：

```shell
uv python list
```

#### 3. 安装后端依赖

下面这组依赖在 Python `3.14.4` 下完成过后端导入和基础接口验证。项目代码使用旧版 LangChain 入口，因此需要固定 `langchain` 相关版本；其他底层依赖交给 `uv` 自动解析适配当前 Python 版本。

```shell
uv pip install \
  fastapi==0.112.2 uvicorn==0.30.6 python-multipart==0.0.20 \
  pandas pypdf pdfplumber PyMuPDF \
  'unstructured[pdf]' chromadb pymilvus pypinyin \
  python-dotenv boto3 \
  langchain==0.3.27 langchain-community==0.3.31 langchain-core==0.3.83 \
  langchain-huggingface==0.3.1 langchain-text-splitters==0.3.11 \
  transformers sentence-transformers accelerate openai requests torch
```

#### 4. 使用 Hugging Face Mirror（推荐）

国内环境建议设置 HF-Mirror：

```shell
export HF_ENDPOINT=https://hf-mirror.com
```

#### 5. 使用本地下载的 HuggingFace 模型（可选步骤）

* 下载 HuggingFace 模型，以 `sentence-transformers/all-MiniLM-L6-v2` 为例：

```shell
# 创建 HF_MODEL_PATH 目录
mkdir -p /Users/yakoo5/hf_model_path
export HF_MODEL_PATH="/Users/yakoo5/hf_model_path"

cd $HF_MODEL_PATH

# 获取 HuggingFace 模型下载脚本
wget https://hf-mirror.com/hfd/hfd.sh
chmod u+x hfd.sh

# 下载 sentence-transformers/all-MiniLM-L6-v2 模型文件
mkdir -p sentence-transformers/all-MiniLM-L6-v2
# 建议上午下载，上午网速较快（10MB/s左右）。大概几分钟左右会被限速（近乎停止），可以终止命令，再重新执行，又可以变成高速下载
./hfd.sh sentence-transformers/all-MiniLM-L6-v2 --tool wget -x 4 -j 1 --local-dir sentence-transformers/all-MiniLM-L6-v2
```

* 设置 HuggingFace 本地模型文件目录 `HF_MODEL_PATH` 环境变量：

```shell
export HF_MODEL_PATH="/Users/yakoo5/hf_model_path"
export HF_ENDPOINT=https://hf-mirror.com
```

#### 6. 配置 OpenAI API Key

根据你使用的命令行工具，在 `~/.bashrc` 或 `~/.zshrc` 中配置 `OPENAI_API_KEY` 环境变量：

```shell
export OPENAI_API_KEY="xxxx"
export DEEPSEEK_API_KEY="xxxx"
```

#### 7. 启动后端

上述开发环境安装完成后，使用 `uvicorn` 启动后端：

```shell
# 进入后端代码目录
cd backend/
# 启动
HF_ENDPOINT=https://hf-mirror.com ../.venv/bin/uvicorn main:app --reload --port 8001 --host 0.0.0.0
```

*(请确保您的后端主文件是 `main.py` 并且 FastAPI 应用实例名为 `app`。如果端口 `8001` 被占用，请更换为其他可用端口。)*

这条命令是使用 Uvicorn 运行一个 ASGI (Asynchronous Server Gateway Interface) 应用程序的指令。让我们分解一下它的各个部分：

- **`uvicorn`**: 这是 Uvicorn 的命令行接口。Uvicorn 是一个闪电般快速的 ASGI 服务器，基于 uvloop 和 httptools 构建。它主要用于运行现代 Python Web 框架，如 FastAPI 和 Starlette。

- **`main:app`**: 这部分指定了要运行的 ASGI 应用程序的位置。

  - **`main`**: 这通常指的是一个名为 `main.py` 的 Python 文件（模块）。

  - `app`: 这指的是在 `main.py` 文件中定义的一个名为 `app`的变量。这个变量应该是一个 ASGI 应用程序实例。例如，如果你在使用 FastAPI，你可能会在  `main.py` 中有类似这样的代码：

    ```python
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    async def read_root():
        return {"Hello": "World"}
    ```

- **`--reload`**: 这是一个非常有用的开发选项。当使用这个标志时，Uvicorn 会监视你的应用程序代码文件的更改。一旦检测到任何更改，它会自动重新启动服务器。这使得在开发过程中可以快速迭代，而无需手动停止和启动服务器。

- **`--port 8001`**: 这个选项指定了 Uvicorn 服务器应该监听的网络端口。在这里，服务器将被配置为在 `8001` 端口上接收传入的 HTTP 请求。如果不指定端口，Uvicorn 默认会使用 `8000` 端口。

**总而言之，这条命令的作用是：**

启动 Uvicorn ASGI 服务器，加载 `main.py` 文件中名为 `app` 的 ASGI 应用程序。服务器将在 `8001` 端口上监听传入的请求，并且在应用程序代码发生更改时自动重新加载。

这通常是在开发基于 ASGI 框架（如 FastAPI 或 Starlette）构建的 Web 应用程序时启动服务器的标准命令。


## 技术架构

### 技术栈
- 后端：Python FastAPI
- 向量数据库：Milvus
- 前端：React + Vite
- 后端：Python 

## 项目架构 

### 后端项目架构 
```
bac
├── main.py                                 # 主入口文件
│
├── services/                               # 服务层目录
│   ├── archive/                           # 归档服务目录
│   │   └── vector_store_service_langchain.py  # LangChain向量存储实现
│   │
│   ├── chunking_service.py                # 文本分块服务
│   ├── embedding_service.py               # 文本嵌入服务
│   ├── generation_service.py              # 内容生成服务
│   ├── loading_service.py                 # 数据加载服务
│   ├── parsing_service.py                 # 文本解析服务
│   ├── search_service.py                  # 搜索服务
│   └── vector_store_service.py            # 向量存储基础服务
│
└── utils/                                 # 工具目录
    └── config.py                          # 配置文件
```
### 前端项目架构 
```
frontend/
├── public/                # 静态资源目录
│   └── vite.svg          # Vite logo
├── src/                  # 源代码目录
│   ├── assets/          # 项目资源文件(图片、字体等)
│   ├── components/      # 可复用的 React 组件
│   ├── pages/           # 页面级组件
│   ├── App.css         # App 组件样式
│   ├── App.jsx         # 根组件
│   ├── index.css       # 全局样式
│   └── main.jsx        # 应用入口文件
├── .gitignore           # Git 忽略文件配置
├── eslint.config.js     # ESLint 代码规范配置
├── index.html          # 项目 HTML 模板
├── note.txt            # 项目笔记
├── package.json        # 项目依赖和脚本配置
├── package-lock.json   # 依赖版本锁定文件
├── postcss.config.js   # PostCSS 配置
├── README.md          # 项目说明文档
├── tailwind.config.js  # Tailwind CSS 配置
└── vite.config.js     # Vite 构建工具配置 
```

## 常见部署异常

### 1. vite报错

```bash
npm run dev

> frontend-241123@0.0.0 dev
> vite

file:///root/AI-Box/code/rag/rag-project01-framework/frontend/node_modules/vite/bin/vite.js:7
    await import('source-map-support').then((r) => r.default.install())
    ^^^^^

SyntaxError: Unexpected reserved word
    at Loader.moduleStrategy (internal/modules/esm/translators.js:133:18)
    at async link (internal/modules/esm/module_job.js:42:21)
```

这个错误通常是因为 Node.js 版本过低导致的。Vite 需要 Node.js 14.18+ 或 16+ 版本才能正常运行。让我们来解决这个问题：

1. 首先，检查当前 Node.js 版本：
```bash
node -v
```

2. 如果版本低于要求，我们需要更新 Node.js。以下是几种更新方法：

方法 1：使用 nvm（Node Version Manager）安装新版本（推荐）：
```bash
# 如果还没有安装 nvm，先安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载 shell 配置
source ~/.bashrc  # 或 source ~/.zshrc

# 安装最新的 LTS 版本的 Node.js
nvm install --lts

# 使用新安装的版本
nvm use --lts
```

方法 2：直接通过包管理器更新（以 Ubuntu/Debian 为例）：
```bash
# 添加 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# 安装 Node.js
sudo apt-get install -y nodejs
```

3. 安装完新版本后，验证版本：
```bash
node -v
npm -v
```

4. 然后重新安装项目依赖：
```bash
cd /path/to/your/frontend/project
rm -rf node_modules package-lock.json
npm install
```

5. 最后重新启动项目：
```bash
npm run dev
```

这样应该就能解决启动错误的问题了。如果还有其他问题，请告诉我具体的错误信息。
