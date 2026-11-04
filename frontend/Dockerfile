# ==============================================================================
# Stage 1: Builder (compilación del bundle de producción de React con Vite)
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Habilitar pnpm mediante Corepack según especificación
RUN corepack enable pnpm

# Copiar manifiestos y configuraciones de pnpm
COPY package.json pnpm-lock.yaml .npmrc* pnpm-workspace.yaml* ./

# Instalar dependencias exactas y reproducibles
RUN pnpm install --frozen-lockfile

# Copiar código fuente
COPY . .

# Compilar los estáticos de producción optimizados
RUN pnpm run build

# ==============================================================================
# Stage 2: Runtime (servidor Nginx ultra liviano para producción)
# ==============================================================================
FROM nginx:alpine AS runtime

# Configuración de Nginx con SPA fallback y proxy /api/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar exclusivamente el bundle compilado desde el builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Healthcheck nativo de Nginx para Docker Compose
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
