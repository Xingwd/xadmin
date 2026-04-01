# 前端

前端使用 [Vite](https://vitejs.dev/)、[Vue](https://vuejs.org)、[Vue Router](https://router.vuejs.org/)、[TypeScript](https://www.typescriptlang.org/)、[Pinia](https://pinia.vuejs.org/)、[Pinia Colada](https://pinia-colada.esm.dev/) 和 [Element Plus](https://element-plus.org) 构建。

## 前端开发

### 使用本地环境开发

在开始之前，请确保你的系统上安装了 Node Version Manager（nvm）或 Fast Node Manager（fnm）。

- 要安装 `fnm`，请遵循 [official fnm guide](https://github.com/Schniz/fnm#installation)。如果你更喜欢 `nvm`，可以遵循 [official nvm guide](https://github.com/nvm-sh/nvm#installing-and-updating) 进行安装。

- 安装 `nvm` 或 `fnm` 后，进入 `frontend` 目录：

```bash
cd frontend
```

- 如果 `.nvmrc` 文件中指定的 Node.js 版本未安装在你的系统上，你可以使用适当的命令安装它：

```bash
# If using fnm
fnm install

# If using nvm
nvm install
```

- 一旦安装完成，切换到已安装的版本：

```bash
# If using fnm
fnm use

# If using nvm
nvm use
```

- 安装 [pnpm](https://pnpm.io)：

```bash
npm install -g pnpm@latest-10
```

- 在 `frontend` 目录中，安装必要的 NPM 包：

```bash
pnpm install
```

- 并使用以下 `pnpm` 脚本启动实时服务器：

```bash
pnpm run dev
```

- 然后在浏览器打开 <http://localhost:5173/>。

请注意，此实时服务器并非在 Docker 中运行，它用于本地环境开发，这是推荐的工作流程。一旦你对前端满意，可以构建前端 Docker 镜像并启动它，以便在类似生产环境中进行测试。但是，每次更改都构建镜像不如使用具有实时重新加载功能的本地开发服务器高效。

检查文件 `package.json` 以查看其他可用选项。

### 使用容器环境开发

使用 Docker Compose 启动本地堆栈：

```bash
docker compose watch
```

**注意**：此命令启动的前端开发环境，使用的指令是 `vite --host 0.0.0.0`。

### 国际化语言包

支持按需加载语言包，配置方式有两种：

- 在 `./frontend/src/lang/zh-cn/` 和 `./frontend/src/lang/en/` 等语言包目录下按照路由path或name创建对应的语言包文件。例如：路由path是 `/system/rules`，则需要创建 `./frontend/src/lang/zh-cn/system/rules.ts` 和 `./frontend/src/lang/en/system/rules.ts` 等语言包。

- 在 `./frontend/src/lang/autoload.ts` 文件中配置路由path和语言包列表的映射关系：

```typescript
{
    '/system/operation-logs': ['./${lang}/system/operationLogs.ts'],
    '/routine/user-info': ['./${lang}/routine/userInfo.ts', './${lang}/system/users.ts'],
}
```

### 移除前端

如果你正在开发一个仅提供 API 的应用程序并且想要移除前端，你可以很容易地做到：

- 删除 `./frontend` 目录。

- 在 `docker-compose.yml` 文件，删除整个 `frontend` 服务/部分。

- 在 `docker-compose.override.yml` 文件，删除整个 `frontend` 服务/部分。

完成后，你拥有了一个没有前端（仅 API）的应用程序。🤓

---

如果你愿意，你也可以从以下位置删除 `FRONTEND` 环境变量：

- `.env`
- `./scripts/*.sh`

但这只是为了清理它们，留下它们也不会有任何影响。

## 生成客户端

### 自动

- 激活后端虚拟环境。
- 从项目顶级目录运行以下脚本：

```bash
./scripts/generate-client.sh
```

- 提交更改。

### 手动

- 启动 Docker Compose 堆栈。

- 从 `http://localhost/api/v1/openapi.json` 下载 OpenAPI JSON 文件，并将其复制到 `frontend` 目录下的新文件 `openapi.json` 中。

- 生成前端客户端，请运行：

```bash
pnpm run generate-client
```

- 提交更改。

请注意，每次后端发生更改（更改 OpenAPI schema）时，你都应该再次执行这些步骤以更新前端客户端。

## 使用远程 API

如果您想使用远程 API，可以将环境变量 `VITE_API_URL` 设置为远程 API 的 URL。例如，您可以在 `frontend/.env` 文件中进行设置：

```env
VITE_API_URL=https://api.my-domain.example.com
```

然后，当你运行前端时，它将把那个 URL 作为 API 的基础 URL。

## 代码结构

前端代码结构如下：

- `frontend/src` - 主要的前端代码。
- `frontend/src/assets` - 静态资源。
- `frontend/src/client` - 生成的 OpenAPI 客户端。
- `frontend/src/components` - 前端的各种组件。
- `frontend/src/lang` - 国际化语言包。
- `frontend/src/layouts` - 布局及相关组件。
- `frontend/src/router` - 路由。
- `frontend/src/stores` - 状态存储。
- `frontend/src/styles` - 样式风格。
- `frontend/src/utils` - 工具。
- `frontend/src/views` - 页面视图。
- `frontend/types` - 全局类型。
