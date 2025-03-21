# 部署

你可以使用 Docker Compose 将项目部署到远程服务器。

这个项目希望你有一个 Traefik 代理来处理与外部世界的通信和 HTTPS 证书。

但是你必须先配置几件事情。🤓

## 准备

* 有一个远程服务器准备好并可用。
* 配置你的域名的 DNS 记录，使其指向你刚刚创建的服务器的 IP。
* 为你的域名配置一个通配符子域名，以便你可以为不同的服务拥有多个子域名，例如 `*.fastapi-project.example.com`。这对于访问不同的组件很有用，比如 `dashboard.fastapi-project.example.com`、`api.fastapi-project.example.com`、`traefik.fastapi-project.example.com` 等。同时对于 `staging` 也很有用，比如 `dashboard.staging.fastapi-project.example.com` 等。
* 在远程服务器上安装和配置 Docker （是 Docker Engine，不是 Docker Desktop）。

## 公共 Traefik

我们需要一个 Traefik 代理来处理传入的连接和 HTTPS 证书。

接下来的这些步骤，你只需要做一次。

### Traefik Docker Compose

* 创建一个远程目录来存储你的 Traefik Docker Compose 文件：

```bash
mkdir -p /root/code/traefik-public/
```

将 Traefik Docker Compose 文件复制到你的服务器。你可以在本地终端中运行命令 `rsync` 来实现这一点：

```bash
rsync -a docker-compose.traefik.yml root@your-server.example.com:/root/code/traefik-public/
```

### Traefik Public Network

此 Traefik 将期望名为 `traefik-public` 的 Docker "public network" 与你的堆栈进行通信。

这样，就会有一个单一的公共 Traefik 代理来处理与外界的通信（HTTP 和 HTTPS），然后在其背后，你可以有一个或多个具有不同域的堆栈，即使它们在同一台服务器上。

要在远程服务器中创建一个名为 `traefik-public` 的 Docker "public network"，请运行以下命令：

```bash
docker network create traefik-public
```

### Traefik 环境参数

Traefik 的 Docker Compose 文件期望在启动之前在你的终端中设置一些环境变量。你可以通过在你的远程服务器上运行以下命令来实现：

* 创建用于 HTTP 基本认证的用户名，例如：

```bash
export USERNAME=admin
```

* 创建一个带有 HTTP 基本认证密码的环境变量，例如：

```bash
export PASSWORD=changethis
```

* 使用 openssl 生成用于 HTTP 基本身份验证的密码的哈希版本，并将其存储在环境变量中：

```bash
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
```

要验证哈希密码是否正确，你可以打印它：

```bash
echo $HASHED_PASSWORD
```

* 创建一个包含服务器域名的环境变量，例如：

```bash
export DOMAIN=fastapi-project.example.com
```

* 创建一个用于 [Let's Encrypt](https://letsencrypt.org/) 的电子邮件的环境变量，例如：

```bash
export EMAIL=admin@example.com
```

**注意**: 你需要设置一个不同的电子邮件地址，一个 `@example.com` 的电子邮件地址是不行的。

### 启动 Traefik Docker Compose

转到在远程服务器中复制 Traefik Docker Compose 文件的目录：

```bash
cd /root/code/traefik-public/
```

现在环境变量已设置，并且 `docker-compose.traefik.yml` 已就绪，您可以通过以下命令启动 Traefik Docker Compose：

```bash
docker compose -f docker-compose.traefik.yml up -d
```

## 部署 FastAPI 项目

现在你已经安装了 Traefik，就可以使用 Docker Compose 部署你的 FastAPI 项目了。

### 环境变量

你需要先设置一些环境变量。

设置 `ENVIRONMENT`，默认情况下为 `local`（用于开发），但是当部署到服务器时，你可以设置为 `staging` 或 `production` 环境:

```bash
export ENVIRONMENT=production
```

设置 `DOMAIN`，默认情况下是 `localhost`（用于开发），但是在部署时，你将使用自己的域名，例如：

```bash
export DOMAIN=fastapi-project.example.com
```

你可以设置几个变量，比如：

* `PROJECT_NAME`: 项目的名称，在API文档和前端站点中使用。
* `STACK_NAME`: 用于 Docker Compose 标签和项目名称的栈名称，对于 `staging`、`production` 等应该不同。你可以使用相同的域，用破折号替换点，例如 `fastapi-project-example-com` 和 `staging-fastapi-project-example-com`。
* `BACKEND_CORS_ORIGINS`: 以逗号分隔的允许的 CORS 源列表。
* `SECRET_KEY`: FastAPI 项目的密钥，用于签署令牌。
* `FIRST_SUPERUSER`: 第一个超级用户的用户名，这个超级用户将是可以创建新用户的人。
* `FIRST_SUPERUSER_PASSWORD`: 第一个超级用户的密码。
* `POSTGRES_SERVER`: PostgreSQL 服务器的主机名。可以保留默认值 `db`，这是由同一个 Docker Compose 提供的。通常情况下，除非使用第三方提供商，否则不需要更改此设置。
* `POSTGRES_PORT`: PostgreSQL 服务器的端口。可以保留默认值。通常情况下，除非你正在使用第三方提供商，否则不需要更改这个值。
* `POSTGRES_PASSWORD`: Postgres 密码。
* `POSTGRES_USER`: Postgres 用户，你可以保留默认值。
* `POSTGRES_DB`: 此应用程序要使用的数据库名称。可以保留默认值 `app`。

### 生成秘钥

`.env` 文件中的一些环境变量的默认值为 `changethis`。

你必须使用一个密钥来更改它们，要生成密钥，你可以运行以下命令：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制内容并将其用作密码/密钥。然后再次运行以生成另一个安全密钥。

### 使用 Docker Compose 部署

有了环境变量，你就可以使用 Docker Compose 进行部署了：

```bash
docker compose -f docker-compose.yml up -d
```

对于生产环境，你不会希望在 `docker-compose.override.yml` 中有覆盖项，这就是为什么我们明确指定 `docker-compose.yml` 作为要使用的文件。

## URLs

将 `fastapi-project.example.com` 替换为你的域名。

### 主 Traefik Dashboard

Traefik UI: `https://traefik.fastapi-project.example.com`

### 生产环境

前端：`https://dashboard.fastapi-project.example.com`

后端 API docs：`https://api.fastapi-project.example.com/docs`

后端 API base URL：`https://api.fastapi-project.example.com`

### 预发布环境

前端：`https://dashboard.staging.fastapi-project.example.com`

后端 API docs：`https://api.staging.fastapi-project.example.com/docs`

后端 API base URL：`https://api.staging.fastapi-project.example.com`
