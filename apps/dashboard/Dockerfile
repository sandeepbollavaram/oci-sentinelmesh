FROM node:20-alpine

ENV VITE_API_BASE_URL=http://127.0.0.1:8000

WORKDIR /app

COPY apps/dashboard/package*.json ./
RUN npm ci

COPY apps/dashboard/ ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
