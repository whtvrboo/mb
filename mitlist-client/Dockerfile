FROM node:20-alpine AS builder

WORKDIR /app

# Enable Corepack for pnpm/yarn if needed
# If using npm, standard install is fine.
COPY package.json package-lock.json* ./

RUN npm ci

COPY . .

RUN npm run build

# Runner stage
FROM node:20-alpine AS runner

WORKDIR /app

# Copy the built output from the builder stage
COPY --from=builder /app/.output /app/.output

# Expose the listening port
EXPOSE 3000

# Set host to 0.0.0.0 to allow external access
ENV HOST=0.0.0.0
ENV PORT=3000

# Run the application
CMD ["node", ".output/server/index.mjs"]
