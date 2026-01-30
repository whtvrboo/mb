FROM python:3.11-slim-bookworm

# Install uv. Use the official install script or copy from the official image.
# Copying from the official image is often cleaner if available, but installing via pip is also fine for slim.
# Actually, the recommended way for purely using uv is:
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the lock file and pyproject.toml
COPY uv.lock pyproject.toml /app/

# Install dependencies using uv
# --frozen ensures we use the exact versions in uv.lock
# --no-install-project installs only dependencies, not the project itself yet (good for caching)
RUN uv sync --frozen --no-install-project

# Copy the rest of the application code
COPY . /app/

# Install the project itself
RUN uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "mitlist.main:app", "--host", "0.0.0.0", "--port", "8000"]
