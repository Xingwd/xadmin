#!/bin/sh -e
set -x

# format backend
(cd backend && bash scripts/format.sh)

# format frontend
(cd frontend && pnpm run format)
