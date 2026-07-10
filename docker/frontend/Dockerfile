FROM node:20-alpine

WORKDIR /app

ENV NODE_OPTIONS=--max-old-space-size=3072

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
