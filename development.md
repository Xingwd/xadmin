# 开发说明

## Docker Compose

* 使用 Docker Compose 启动本地堆栈：

```bash
docker compose watch
```

* 现在你可以打开浏览器并与以下这些 URL 进行交互：

前端，使用 Docker 构建，根据路径处理路由：http://localhost:5173

后端，基于 OpenAPI 的基于 JSON 的 Web API：http://localhost:8000

带有 Swagger UI 的自动交互式文档（来自 OpenAPI 后端）：http://localhost:8000/docs

Traefik UI，用于查看代理如何处理路由：http://localhost:8090

**注意**：首次启动堆栈时，可能需要一分钟才能准备就绪。在此期间，后端等待数据库准备好并配置所有内容。你可以查看日志以进行监控。

要检查日志，请运行（在另一个终端中）：

```bash
docker compose logs
```

要检查特定服务的日志，请添加服务的名称，例如：

```bash
docker compose logs backend
```

## 本地开发

Docker Compose 文件已配置为每个服务在 `localhost` 的不同端口上可用。

对于后端和前端，它们使用本地开发服务器将使用的相同端口，因此，后端位于 `http://localhost:8000`，前端位于 `http://localhost:5173`

这样，你可以关闭 Docker Compose 服务并启动其本地开发服务，并且一切都会继续正常工作，因为它们都使用相同的端口。

例如，你可以在 Docker Compose 中停止那个 `frontend` 服务，在另一个终端中，运行：

```bash
docker compose stop frontend
```

然后启动本地前端开发服务器：

```bash
bun run dev
```

或者你可以停止 Docker Compose 中的 `backend` 服务。

```bash
docker compose stop backend
```

然后你可以为后端运行本地开发服务器：

```bash
cd backend
fastapi dev app/main.py
```

## Docker Compose in `localhost.xadmin.com`

当你启动 Docker Compose 堆栈时，它默认使用 `localhost`，每个服务（后端、前端 等）使用不同的端口。

当你将其部署到生产环境（或预发布环境）时，它会将每个服务部署在不同的子域中，例如后端为 `api.example.com`，前端为 `dashboard.example.com`。

在关于 [deployment](deployment.md) 的指南中，你可以阅读有关 Traefik 的内容，它是已配置的代理。这是一个根据子域将流量传输到每个服务的组件。

如果您想在本地测试一切是否正常工作，可以编辑本地 `.env` 文件，并更改：

```dotenv
DOMAIN=localhost.xadmin.com
FRONTEND_HOST=http://dashboard.localhost.xadmin.com
```

这将被 Docker Compose 文件用于配置服务的基础域。

Traefik 将使用此功能将 `api.localhost.xadmin.com` 的流量传输到后端，并将 `dashboard.localhost.xadmin.com` 的流量传输到前端。

域名 `localhost.xadmin.com` 是一个特殊的域名，配置其（包括其所有子域名）指向 `127.0.0.1`。这样你就可以在本地开发中使用它。

更新后再次运行：

```bash
docker compose watch
```

部署时，例如在生产环境中，主 Traefik 是在 Docker Compose 文件之外进行配置的。对于本地开发，在 `compose.override.yml` 中有一个包含的 Traefik，只是为了让你测试域是否按预期工作，例如使用 `api.localhost.xadmin.com` 和 `dashboard.localhost.xadmin.com`。

## Docker Compose 文件和环境参数

有一个主要的 `compose.yml` 文件，其中包含适用于整个堆栈的所有配置，它由 `docker compose` 自动使用。

还有一个 `compose.override.yml` 文件，其中包含开发环境的覆盖配置，例如将源代码挂载为卷。`docker compose` 会自动应用它，覆盖 `compose.yml` 的配置。

这些 Docker Compose 文件使用 `.env` 文件，该文件包含的配置将作为环境变量注入到容器中。

他们还使用了一些额外的配置，这些配置是在调用 `docker compose` 命令之前从脚本中设置的环境变量中获取的。

在更改变量后，请确保重新启动堆栈：

```bash
docker compose watch
```

## .env 文件

`.env` 文件包含你所有的配置、生成的密钥和密码等内容。

根据你的工作流程，你可能希望将其从 Git 中排除，例如，如果你的项目是公开的。在这种情况下，你必须确保设置一种方法，让你的持续集成工具在构建或部署项目时能够获取它。

一种方法是将每个环境变量添加到你的持续集成/持续部署（CI/CD）系统中，并更新 `compose.yml` 文件以读取那个特定的环境变量，而不是读取 `.env` 文件。

## 前置提交钩子与代码静态检查

我们使用一款名为 [prek](https://prek.j178.dev/) 的工具进行代码检查与代码格式化，它是 [Pre-commit](https://pre-commit.com/) 的现代化替代方案。

安装该工具后，它会在 Git 执行代码提交操作前自动运行。借此确保代码在提交前就统一编码风格、完成格式化。

项目根目录下存有配置文件 `.pre-commit-config.yaml`。

### 安装prek自动运行

`prek` 已被纳入本项目依赖项。

完成 `prek` 工具安装并配置可用后，还需在本地代码仓库中执行初始化安装，使其在每次代码提交前自动触发运行。

借助包管理工具 `uv` 可执行下述命令（请确认当前工作目录位于 `backend` 文件夹内）：

```bash
❯ uv run prek install -f
prek installed at `../.git/hooks/pre-commit`
```

参数 `-f` 用于强制安装，适用于本地此前已经安装过 `pre-commit` 钩子的场景。

此后每当你执行代码提交操作，例如使用如下命令：

```bash
git commit
```

`prek` 会自动执行，在提交代码之前进行校验与格式化处理；若代码被改动，会要求你重新通过 Git 暂存代码后再提交。

之后你再次执行 `git add` 命令添加修改修复后的文件，即可正常提交代码。

### 手动执行prek钩子

你也可以使用 `uv` 手动对全部文件执行 `prek` 校验，执行命令如下：

```bash
❯ uv run prek run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
eslint fix...............................................................Passed
prettier format..........................................................Passed
vue-tsc typecheck........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
mypy check...............................................................Passed
ty check.................................................................Passed
Generate Frontend SDK....................................................Passed
```

## URLs

生产或预发布环境的 URL 将使用相同的路径，但使用不同的域名。

### 开发环境 URLs

本地开发环境 URLs。

前端：http://localhost:5173

后端：http://localhost:8000

自动交互文档 (Swagger UI)：http://localhost:8000/docs

Traefik UI：http://localhost:8090

### 配置 `localhost.xadmin.com` 的开发环境 URLs

本地开发环境 URLs。

前端: http://dashboard.localhost.xadmin.com

后端: http://api.localhost.xadmin.com

自动交互文档 (Swagger UI)：http://api.localhost.xadmin.com/docs

Traefik UI：http://localhost.xadmin.com:8090
