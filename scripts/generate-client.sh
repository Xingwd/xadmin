#! /usr/bin/env bash

set -e
set -x

# 生成openapi.json
(cd backend && python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../frontend/openapi.json)
# 生成客户端
(cd frontend && pnpm run generate-client)
