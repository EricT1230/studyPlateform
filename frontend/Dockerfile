# Frontend — Vite build, served by nginx (build context is ./frontend)

# --- Stage 1: build the static SPA ---
FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Same-origin API: client calls /api/*, nginx proxies to the backend.
# (frontend/.env is excluded via .dockerignore so this value wins.)
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

# --- Stage 2: serve with nginx ---
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
