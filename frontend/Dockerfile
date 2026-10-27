# Dockerfile simple para el frontend en desarrollo (React + Vite + pnpm)
# Sin multi-stage según consigna del Ticket T4
FROM node:22-alpine

WORKDIR /app

# Habilitamos pnpm
RUN npm install -g pnpm

# Copiamos archivos de dependencias y configuración de pnpm (incluyendo aprobaciones de builds)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml* ./

# Instalamos las dependencias
RUN pnpm install

# Copiamos el resto del código fuente
COPY . .

# Exponemos el puerto de desarrollo de Vite
EXPOSE 5173

# Iniciamos Vite en 0.0.0.0 para ser accesible desde el navegador del host
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
