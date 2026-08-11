# Stage 1: Build the frontend
FROM node:20-slim as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for some python packages)
# RUN apt-get update && apt-get install -y ...

# Copy python requirements
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the Python package layout used by local development and tests.
COPY server/ /app/server/

# Copy built frontend from build stage
COPY --from=build /app/dist /app/static

# Expose port (Render uses PORT env var, but 8080 is standard default)
EXPOSE 8080

# Render injects PORT. Keep 8080 as the local/container default.
CMD ["sh", "-c", "uvicorn server.server:app --host 0.0.0.0 --port ${PORT:-8080}"]
