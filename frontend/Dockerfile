# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:20 AS build-stage

WORKDIR /app

COPY package*.json pnpm-lock.yaml /app/

RUN npm install -g pnpm@latest-10
RUN pnpm install

COPY ./ /app/

ARG VITE_SITE_URL=${VITE_SITE_URL}
ARG VITE_API_URL=${VITE_API_URL}

RUN pnpm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
