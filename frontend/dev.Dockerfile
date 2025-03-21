# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:20 AS build-stage

WORKDIR /app

COPY package*.json pnpm-lock.yaml /app/

RUN npm install -g pnpm@latest-10
RUN pnpm install

COPY ./ /app/

ARG VITE_SITE_URL=${VITE_SITE_URL}
ARG VITE_API_URL=${VITE_API_URL}

CMD ["pnpm", "run", "dev-in-container"]
