# 前端

前端使用 [Vite](https://vitejs.dev/)、[Vue](https://vuejs.org)、[Vue Router](https://router.vuejs.org/)、[TypeScript](https://www.typescriptlang.org/)、[Pinia](https://pinia.vuejs.org/)、[Pinia Colada](https://pinia-colada.esm.dev/) 和 [Element Plus](https://element-plus.org) 构建。

## 开发前提

- [Bun](https://bun.sh/) (推荐) 或 [Node.js](https://nodejs.org/)

## 快速开始

进入frontend目录，执行：

```bash
bun install
bun run dev
```

- 然后在浏览器打开 <http://localhost:5173/>。

请注意，此实时服务器并非在 Docker 中运行，它用于本地环境开发，这是推荐的工作流程。一旦你对前端满意，可以构建前端 Docker 镜像并启动它，以便在类似生产环境中进行测试。但是，每次更改都构建镜像不如使用具有实时重新加载功能的本地开发服务器高效。

检查文件 `package.json` 以查看其他可用选项。

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

- 在 `compose.yml` 文件，删除整个 `frontend` 服务/部分。

- 在 `compose.override.yml` 文件，删除整个 `frontend` 服务/部分。

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
bash ./scripts/generate-client.sh
```

- 提交更改。

### 手动

- 启动 Docker Compose 堆栈。

- 从 `http://localhost/api/v1/openapi.json` 下载 OpenAPI JSON 文件，并将其复制到 `frontend` 目录下的新文件 `openapi.json` 中。

- 生成前端客户端，请运行：

```bash
bun run generate-client
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

## 使用Playwright进行端到端测试

前端项目内置了基于 Playwright 编写的初步端到端测试。执行测试前，需先启动 Docker Compose 整套服务环境，使用下述命令启动服务集群：

```bash
docker compose up -d --wait backend
```

之后，你可以在项目根目录，通过下面的命令执行测试：

```bash
bun run test
```

你也可以通过 UI 可视化模式运行测试，实时查看浏览器运行画面并与其交互。

```bash
bun run test:ui
```

如需停止并移除 Docker Compose 服务集群并清理测试过程中生成的数据，执行以下命令：

```bash
docker compose down -v
```

如需更新测试用例，进入测试目录，按需修改现有测试文件或新增测试文件。

如需了解更多编写与运行 Playwright 测试的相关内容，请查阅官方文档：[Playwright documentation](https://playwright.dev/docs/intro)。
