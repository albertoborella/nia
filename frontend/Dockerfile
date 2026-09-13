# Stage 1: Build
FROM public.ecr.aws/docker/library/node:22-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

RUN npm run build

# Stage 2: Run
FROM public.ecr.aws/docker/library/node:22-slim AS runner

WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .

ENV PORT=3000
EXPOSE 3000
CMD ["node", "build"]
