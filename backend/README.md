# 后端

## 要求

- [Docker](https://www.docker.com/)。
- [uv](https://docs.astral.sh/uv/) 用于 Python 包和环境管理。

## Docker Compose

按照 [../development.md](../development.md) 中的指南使用 Docker Compose 启动本地开发环境。

## 一般工作流

默认情况下，依赖项由 [uv](https://docs.astral.sh/uv/) 管理。

从 `./backend/` 你可以使用以下命令安装所有依赖项：

```console
uv sync
```

然后你可以使用以下命令激活虚拟环境：

```console
source .venv/bin/activate
```

确保你的编辑器正在使用正确的 Python 虚拟环境，解释器位于 `backend/.venv/bin/python`。

在 `./backend/app/models/` 中修改或添加 SQLModel 模型，在 `./backend/app/api/` 中修改或添加 API 端点，在 `./backend/app/crud/` 中修改或添加 CRUD (Create, Read, Update, Delete) 工具。

## VS Code

已有配置可通过 VS Code 调试器运行后端，以便你可以使用断点、暂停并探索变量等。

设置也已经配置好，因此你可以通过 VS Code 的 Python 测试选项卡运行测试。

## Docker Compose Override

在开发过程中，你可以在文件 `docker-compose.override.yml` 中更改仅影响本地开发环境的 Docker Compose 设置。

对该文件的更改仅影响本地开发环境，而非生产环境。因此，你可以添加有助于开发工作流程的“临时”更改。

例如，包含后端代码的目录在 Docker 容器中是同步的，将你更改的代码实时复制到容器内的目录中。这使你可以立即测试你的更改，而无需再次构建 Docker 镜像。这只应在开发期间进行，对于生产环境，你应该使用最新版本的后端代码构建 Docker 镜像。但在开发期间，它允许你非常快速地进行迭代。

还有一个命令覆盖项，它运行 `fastapi run --reload` 而不是默认的 `fastapi run`。它启动单个服务器进程（而不是像生产环境中那样启动多个），并且每当代码更改时就重新加载进程。请记住，如果你有语法错误并保存 Python 文件，它将崩溃并退出，容器也将停止。之后，你可以通过修复错误并再次运行来重新启动容器：

```console
docker compose watch
```

还有一个被注释掉的 `command` 覆盖项，你可以取消注释它并注释掉默认的那个。它使后端容器运行一个“什么都不做”的进程，但保持容器处于活动状态。这允许你进入正在运行的容器并在其中执行命令，例如一个 Python 解释器来测试已安装的依赖项，或者启动在检测到更改时重新加载的开发服务器。

要使用 `bash` 会话进入容器，可以使用以下方式启动堆栈：

```console
docker compose watch
```

然后在另一个终端中，在正在运行的容器中执行 `exec` ：

```console
docker compose exec backend bash
```

你应该看到这样的输出：

```console
root@7f2607af31c3:/app#
```

这意味着你在容器内处于一个 `bash` 会话中，作为 `root` 用户，在 `/app` 目录下，这个目录内有另一个名为“app”的目录，那就是你的代码在容器中的位置：`/app/app`。

在那里，你可以使用 `fastapi run --reload` 命令来运行带有实时重新加载功能的调试服务器。

```console
fastapi run --reload app/main.py
```

……它看起来像：

```console
root@7f2607af31c3:/app# fastapi run --reload app/main.py
```

然后按回车键。这将运行实时重新加载服务器，当检测到代码更改时会自动重新加载。

然而，如果它没有检测到变化而是检测到语法错误，它将因错误而停止。但是由于容器仍然处于活动状态，并且你处于 Bash 会话中，因此在修复错误后，你可以通过运行相同的命令（“上箭头”和“回车”）快速重新启动它。

……前面的细节使得让容器保持存活状态但不执行任何操作是有用的，然后在 Bash 会话中，使其运行实时重新加载服务器。

## 权限

后端已封装权限模型，可根据配置的 `api path` 自动生成 `CRUD` 权限。如需增加或修改权限，可修改 `./backend/app/core/security.py` 文件中的 `ApiPermissions` 枚举类。

定义好权限后，即可通过 `Security scopes` 使用权限，示例：

```python
Security(get_current_user, scopes=[ApiPermissions.V1_RULES.value.read.name])
```

## 后端测试

要测试后端，请运行：

```console
bash ./scripts/test.sh
```

这些测试使用 Pytest 运行，修改并向 `./backend/app/tests/` 添加测试。

### 测试运行中的堆栈

如果你的堆栈已经启动，而你只是想运行测试，你可以使用：

```bash
docker compose exec backend bash scripts/tests-start.sh
```

`/app/scripts/tests-start.sh` 脚本在确保其余部分的堆栈正在运行后，仅调用 `pytest`。如果你需要向 `pytest` 传递额外的参数，你可以将它们传递给那个命令，它们将会被转发。

例如，要在第一个错误处停止：

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### 测试覆盖率

当测试运行时，会生成一个文件 `htmlcov/index.html`，你可以在浏览器中打开它以查看测试的覆盖率。

## 数据库模型版本迁移

在本地开发期间，由于你的应用程序目录作为卷挂载在容器内部，你也可以在容器内使用 `alembic` 命令运行迁移，并且迁移代码将在你的应用程序目录中（而不是仅在容器内部）。因此，你可以将其添加到你的 Git 存储库中。

确保你为模型创建一个 `revision`，并且每次更改模型时都使用该修订版 `upgrade` 你的数据库。因为这是更新数据库中表的方式。否则，你的应用程序将出现错误。

- 在后端容器中启动一个交互式会话：

```console
docker compose exec backend bash
```

- Alembic 已经配置为从 `./backend/app/models/` 导入你的 SQLModel 模型。如果新增数据库表模型，需要在 `./backend/app/models/__init__.py` 中导入，Alembic 才能检测到新模型，示例如下：

```python
# for 'alembic autogenerate' support
from . import link, operation_log, role, rule, security, user # noqa
```

- 更改模型后（例如，添加一列），在容器内创建一个 `revision`，例如：

```console
alembic revision --autogenerate -m "Add column last_name to User model"
```

- 将在 alembic 目录中生成的文件提交到 Git 仓库。

- 创建 `revision` 后，在数据库中运行迁移（这将实际更改数据库）：

```console
alembic upgrade head
```

如果你不想使用迁移，请在文件 `./backend/app/core/db.py` 中取消注释以下内容结尾的行：

```python
SQLModel.metadata.create_all(engine)
```

并对文件 `scripts/prestart.sh` 中包含以下内容的行进行注释：

```console
alembic upgrade head
```

如果你不想从默认模型开始，并且想从一开始就删除它们/修改它们，而没有任何先前的修订版本，你可以删除 `./backend/app/alembic/versions/` 下的修订文件（`.py`  Python 文件）。然后按照上述说明创建第一个迁移。
