# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Instala deps primeiro para cache
COPY package.json ./
RUN npm install

# Copia o resto do código
COPY . .

EXPOSE 3000
# O comando real está no docker-compose: "npm run dev"

